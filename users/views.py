from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import get_user_model
import stripe
import os
from rest_framework.views import APIView

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name',
                    'country', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name',''),
            last_name=validated_data.get('last_name',''),
        )
        user.country=validated_data.get('country','')
        user.role=validated_data.get('role','STUDENT')
        user.save()
        return user


class CreateStripeCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            plan = request.data.get('plan')
            if plan not in ['pro', 'ultra']:
                return Response({"success": False, "error": "Nieprawidłowy plan subskrypcji."}, status=400)

            if plan == 'pro':
                price_id = os.environ.get('STRIPE_PRICE_PRO_ID')
            else:
                price_id = os.environ.get('STRIPE_PRICE_ULTRA_ID')

            if not price_id:
                return Response({
                    "success": False,
                    "error": "Konfiguracja Stripe na serwerze jest niekompletna (brak Price ID)."
                }, status=500)

            frontend_url = request.headers.get('Origin') or "http://localhost:3000"

            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=f"{frontend_url}/dashboard?payment=success",
                cancel_url=f"{frontend_url}/pricing?payment=cancel",
                metadata={
                    'user_id': request.user.id,
                    'plan': plan
                }
            )

            return Response({"success": True, "checkout_url": checkout_session.url})

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            user_id = session.get('metadata', {}).get('user_id')
            plan = session.get('metadata', {}).get('plan')
            stripe_customer_id = session.get('customer')

            if user_id and plan:
                try:
                    user = User.objects.get(id=user_id)
                    user.subscription_plan = plan
                    user.stripe_customer_id = stripe_customer_id



                    user.save()
                    print(f"Sukces! Użytkownik {user.username} ma teraz plan {plan}")
                except User.DoesNotExist:
                    pass

        return HttpResponse(status=200)



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['GET'])
def user(request):
    return Response({"message": "user page"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({"message": "profile page",
                     "username": user.username,
                     "first_name": user.first_name,
                     "last_name": user.last_name,
                     "email": user.email,
                     "country": user.country,
                     "role": user.role,})