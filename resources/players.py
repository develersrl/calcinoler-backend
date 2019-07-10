import logging

from flask import request, current_app
from flask_restful import Resource

from database import db
from models.player import Player, PlayerSchema
from utils.slackhelper import SlackHelper, SlackRequestFailed
from utils.players import enrich_slack_users_with_players
from utils.response import Response

player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


class PlayersResource(Resource):
    def get(self):
        slack = SlackHelper(current_app.config['SLACK_TOKEN'])
        players = Player.query.all()
        try:
            slack_users = slack.get_users(search=request.args.get("s"))
        except SlackRequestFailed as e:
            logging.error('Slack Api Error: {}'.format(str(e)))
            return Response.error({'general': [Response.REQUEST_FAILED]}, 503)
        players = enrich_slack_users_with_players(slack_users, players)

        return Response.success(players_schema.dump(players).data)


class PlayerResource(Resource):
    def get(self, slack_id):
        slack = SlackHelper(current_app.config['SLACK_TOKEN'])
        try:
            slack_user = slack.get_user(slack_id)
        except SlackRequestFailed as e:
            logging.error('Slack Api Error: {}'.format(str(e)))
            return Response.error({'general': [Response.REQUEST_FAILED]}, 503)

        player = Player.query.get(slack_id)
        if player is None:
            player = Player()

        player.merge_slack_user(slack_user)
        return Response.success(player_schema.dump(player).data)

    def patch(self, slack_id):
        slack = SlackHelper(current_app.config['SLACK_TOKEN'])

        try:
            slack_user = slack.get_user(slack_id)
        except SlackRequestFailed as e:
            logging.error('Slack Api Error: {}'.format(str(e)))
            return Response.error({'general': [Response.REQUEST_FAILED]}, 503)

        request_data = request.get_json(force=True)
        if not request_data:
            return Response.error({'general': [Response.BODY_EMPTY]}, 400)

        errors = player_schema.validate(request_data)
        if errors:
            return Response.error(errors, 422)

        player = Player.query.get(slack_id)
        response_code = 200
        if not player:
            player = Player()
            player.slack_id = slack_id
            response_code = 201
            db.session.add(player)

        player_schema.load(request_data, instance=player)

        db.session.commit()
        player.merge_slack_user(slack_user)

        return Response.success(player_schema.dump(player).data, response_code)

    def delete(self, slack_id):
        player = Player.query.get(slack_id)
        if not player:
            return Response.error(
                {'general': [Response.NOT_FOUND.format("Player")]}, 404)
        db.session.delete(player)
        db.session.commit()

        return Response.success(player_schema.dump(player).data)
