from http import HTTPStatus
from marshmallow.exceptions import ValidationError
from flask import Blueprint, request, g
from models.deck import DeckModel
from app import db
from middleware.secure_route import secure_route
from serializers.deck import DeckSerializer


deck_serializer = DeckSerializer()

router = Blueprint("decks", __name__)


@router.route("/decks", methods=["GET"])
def get_decks():

    decks = db.session.query(DeckModel).all()
    return deck_serializer.jsonify(decks, many=True)


@router.route("/decks/<int:deck_id>", methods=["GET"])
def get_single_deck(deck_id):
    # ! Get a single tea using our db and sqlalchemy
    deck = db.session.query(DeckModel).get(deck_id)

    # ! If there's no tea..
    if not deck:
        # ! Send back a response with a message and status code (its a tuple)
        return {"message": "No deck found"}, HTTPStatus.NOT_FOUND

    # ! Serialize the single tea object. This time now need for many=True
    return deck_serializer.jsonify(deck)


@router.route("/decks", methods=["POST"])
@secure_route
def create_decks():

    deck_dictionary = request.json

    try:
        deck_model = deck_serializer.load(deck_dictionary)
        deck_model.user_id = g.current_user.id

        db.session.add(deck_model)
        db.session.commit()

        print("Deck", deck_model, "added")
        return deck_serializer.jsonify(deck_model)

    except ValidationError as e:
        return {
            "errors": e.messages,
            "message": "Something went wrong.",
        }, HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception as e:
        print(e)
        return {"message": "Something went wrong."}, HTTPStatus.INTERNAL_SERVER_ERROR


@router.route("/decks/<int:deck_id>", methods=["PUT"])
@secure_route
def update_tea(deck_id):

    try:

        existing_deck = db.session.query(DeckModel).get(deck_id)

        if not existing_deck:
            return {"message": "No deck found"}, HTTPStatus.NOT_FOUND

        if existing_deck.user_id != g.current_user.id:
            return {
                "message": "This is not your deck! Go make your own deck."
            }, HTTPStatus.UNAUTHORIZED

        deck_dictionary = request.json

        deck = deck_serializer.load(
            deck_dictionary,
            instance=existing_deck,
            partial=True,
        )

        db.session.commit()

        return deck_serializer.jsonify(deck)
    except ValidationError as e:
        return {
            "errors": e.messages,
            "message": "Something went wrong",
        }, HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}, HTTPStatus.INTERNAL_SERVER_ERROR


@router.route("/decks/<int:deck_id>", methods=["DELETE"])
@secure_route
def remove_tea(deck_id):

    deck_to_delete = db.session.query(DeckModel).get(deck_id)

    if not deck_to_delete:
        return {"message": "No deck found"}, HTTPStatus.NOT_FOUND

    if deck_to_delete.user_id != g.current_user.id:
        return {
            "message": "This is not your deck! Go make your own deck."
        }, HTTPStatus.UNAUTHORIZED

    db.session.delete(deck_to_delete)
    db.session.commit()

    print("Deck deleted ...", deck_to_delete)
    return {"message": "Deck deleted."}
