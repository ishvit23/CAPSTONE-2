from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .services.chat_service import ChatService
from .services.mongo_client import mongo_db as get_mongo_db
import logging

logger = logging.getLogger(__name__)

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_service = ChatService()

    def post(self, request, *args, **kwargs):
        try:
            message = request.data.get('message')
            if not message:
                return Response(
                    {"error": "Message is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get chat history if provided
            chat_history = request.data.get('chat_history', [])

            # Fetch Mongo user profile
            mongo_user = get_mongo_db().users.find_one({"email": request.user.email})
            user_mongo_id = str(mongo_user["_id"]) if mongo_user else None
            user_google_id = mongo_user.get("google_id") if mongo_user else None

            # Generate response
            response = self.chat_service(message, chat_history)

            try:
                get_mongo_db().chats.insert_one({
                    "user_id": request.user.id,
                    "user_email": request.user.email,
                    "user_mongo_id": user_mongo_id,
                    "user_google_id": user_google_id,
                    "message": message,
                    "chat_history": chat_history,
                    "response": response.get("response"),
                    "status": response.get("status"),
                    "sources": response.get("sources"),
                    "used_knowledge_base": response.get("used_knowledge_base"),
                    "created_at": timezone.now(),
                })
            except Exception as db_error:
                logger.warning(f"Failed to store chat record: {db_error}")

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in ChatbotView: {str(e)}")
            return Response(
                {
                    "error": "An error occurred while processing your request",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logs = list(
                get_mongo_db().chats.find(
                    {"user_id": request.user.id}
                ).sort("created_at", -1).limit(20)
            )
            for log in logs:
                log["_id"] = str(log["_id"])
            return Response({"chats": logs})
        except Exception as e:
            logger.error(f"Failed to fetch chat history: {e}")
            return Response(
                {"error": "Unable to load chat history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
