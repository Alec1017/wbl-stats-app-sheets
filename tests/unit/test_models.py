from faker import Faker

from app.models import Player


def test_new_user():
    fake = Faker()

    """
    GIVEN a Player model
    WHEN a new Player is created
    THEN check the first name and last name fields are defined correctly
    """

    player = Player(id=1, 
                    first_name='first name', 
                    last_name='last name', 
                    email=fake.ascii_email(),
                    password=fake.lexify('????????'),
                    division=1,
                    admin=False,
                    subscribed=True)

    assert player.first_name == 'first name'
    assert player.last_name == 'last name'

