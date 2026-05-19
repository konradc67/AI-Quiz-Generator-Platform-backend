from rest_framework import generics, serializers, status
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
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'country', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        country = validated_data.pop('country', '')
        role = validated_data.pop('role', 'STUDENT')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        user.country = country
        user.role = role
        user.save()
        return user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # NAPRAWIONE: Zmieniono z is_is_valid() na prawidłowe is_valid()
        if not serializer.is_valid():
            print(f"--- BŁĄD WALIDACJI REJESTRACJI ---")
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
                print("BŁĄD STRIPE: Brak STRIPE_PRICE_PRO_ID lub STRIPE_PRICE_ULTRA_ID w zmiennych środowiskowych Vercela!")
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
            print(f"BŁĄD STRIPE CHECKOUT: {str(e)}")
            return Response({"success": False, "error": str(e)}, status=500)


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

        if not endpoint_secret:
            print("BŁĄD WEBHOOKA: Brak STRIPE_WEBHOOK_SECRET w zmiennych środowiskowych Vercela!")
            return HttpResponse("Webhook secret missing", status=500)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            print(f"BŁĄD WEBHOOKA (ValueError): {str(e)}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(f"BŁĄD WEBHOOKA (SignatureVerificationError): {str(e)}")
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            user_id = session.get('metadata', {}).get('user_id')
            plan = session.get('metadata', {}).get('plan')
            stripe_customer_id = session.get('customer')

            print(f"Otrzymano webhook checkout.session.completed dla User ID: {user_id}, Plan: {plan}")

            if user_id and plan:
                try:
                    user = User.objects.get(id=user_id)
                    user.subscription_plan = plan
                    user.stripe_customer_id = stripe_customer_id
                    user.save()
                    print(f"SUKCES: Użytkownik {user.username} (ID: {user_id}) pomyślnie zaktualizowany do planu {plan}!")
                except User.DoesNotExist:
                    print(f"BŁĄD WEBHOOKA: Stripe zapłacił, ale użytkownik o ID {user_id} nie istnieje w bazie danych!")
                    return HttpResponse("User not found", status=404)
                except Exception as e:
                    print(f"BŁĄD ZAPISU UŻYTKOWNIKA W WEBHOOKU: {str(e)}")
                    return HttpResponse("Database save error", status=500)

        return HttpResponse(status=200)


@api_view(['GET'])
def user(request):
    return Response({"message": "user page"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        "message": "profile page",
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "country": getattr(user, 'country', ''),
        "role": getattr(user, 'role', 'STUDENT'),
    })