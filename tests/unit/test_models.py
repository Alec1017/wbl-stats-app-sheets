import pytest
from faker import Faker

from app import create_app
from app.models import Player
from config import Test


class TestPlayer:

    @pytest.fixture
    def test_app(self, scope='module'):
        return create_app(Test)


    @pytest.fixture
    def player(self, scope='module'):
        """
        Generates a mock Player
        """

        fake = Faker()

        player = Player(id=1, 
                        first_name='first name', 
                        last_name='last name', 
                        email=fake.ascii_email(),
                        password=fake.lexify('????????'),
                        division=1,
                        admin=False,
                        subscribed=True)

        return player


    def test_new_player(self, player):
        """
        Tests a player is created correctly
        """

        assert player.first_name == 'first name'
        assert player.last_name == 'last name'
        assert player.division == 1
        assert player.admin == False
        assert player.subscribed == True


    def test_player_hash(self, player, test_app):
        """
        Tests that a player hash function can correctly encode and decode data
        """
        with test_app.app_context():
            # Generate token that is valid for 10 minutes
            auth_token = player.encode_auth_token(player.id, expiration=600)

            assert auth_token != player.id
            assert Player.decode_auth_token(auth_token) == player.id

