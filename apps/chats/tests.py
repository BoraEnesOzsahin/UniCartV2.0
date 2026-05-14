from django.test import TestCase
from django.contrib.auth.models import User
from listings.models import Listing, Category
from chats.models import Conversation, ConversationMembership, Message
from chats.services import moderate_text, check_rate_limits, apply_strike
from users.models import UserProfile

class MessagingServiceTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='buyer', password='password')
        UserProfile.objects.create(user=self.user1, email_verified=True)
        self.user2 = User.objects.create_user(username='seller', password='password')
        UserProfile.objects.create(user=self.user2, email_verified=True)
        self.category = Category.objects.create(name='Test', slug='test')
        self.listing = Listing.objects.create(
            seller=self.user2,
            title='Test Item',
            description='Test Description',
            price=100,
            category=self.category
        )

    def test_moderation_profanity(self):
        res = moderate_text("You are an idiot")
        self.assertFalse(res.allowed)
        self.assertTrue(res.strike)
        self.assertIn("Offensive language", res.warning)

    def test_moderation_credentials(self):
        res = moderate_text("My password is 123")
        self.assertFalse(res.allowed)
        self.assertIn("password", res.warning)

    def test_moderation_scam(self):
        res = moderate_text("Send money via wire transfer")
        self.assertFalse(res.allowed)
        self.assertIn("scam", res.warning)

    def test_moderation_clean(self):
        res = moderate_text("Is this still available?")
        self.assertTrue(res.allowed)
        self.assertEqual(res.sanitized_text, "Is this still available?")

    def test_rate_limiting(self):
        conv = Conversation.objects.create(listing=self.listing, buyer=self.user1, seller=self.user2)
        membership = ConversationMembership.objects.create(conversation=conv, user=self.user1, role='buyer')
        
        # First message OK
        err = check_rate_limits(membership, conv)
        self.assertIsNone(err)
        
        Message.objects.create(conversation=conv, sender=self.user1, text="Hello")
        
        # Second message too fast
        err = check_rate_limits(membership, conv)
        self.assertEqual(err, 'You are sending messages too quickly. Please slow down.')

    def test_strike_system(self):
        conv = Conversation.objects.create(listing=self.listing, buyer=self.user1, seller=self.user2)
        membership = ConversationMembership.objects.create(conversation=conv, user=self.user1, role='buyer')
        
        apply_strike(membership, "Test")
        apply_strike(membership, "Test")
        apply_strike(membership, "Test")
        
        membership.refresh_from_db()
        self.assertEqual(membership.strikes, 3)
        self.assertTrue(membership.is_muted())

    def test_start_conversation_view(self):
        self.client.login(username='buyer', password='password')
        response = self.client.post(f'/chats/start/{self.listing.id}/')
        self.assertEqual(response.status_code, 302) # Redirect to chat detail
        
        conv = Conversation.objects.get(listing=self.listing, buyer=self.user1)
        self.assertEqual(conv.seller, self.user2)

    def test_cannot_message_self(self):
        self.client.login(username='seller', password='password')
        response = self.client.post(f'/chats/start/{self.listing.id}/')
        self.assertEqual(response.status_code, 302) # Redirect to listing detail
        self.assertFalse(Conversation.objects.filter(listing=self.listing, buyer=self.user2).exists())
