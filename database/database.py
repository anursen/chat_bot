from langchain_core.chat_history import BaseChatMessageHistory
from langchain.schema import BaseChatMessageHistory, ChatMessage, HumanMessage, AIMessage
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from datetime import datetime  # Import the `datetime` module for `datetime.utcnow`
from sqlalchemy.orm import declarative_base, sessionmaker

# Define SQLAlchemy ORM Base
Base = declarative_base()


# Define a ChatMessage Model for SQLAlchemy
class ChatMessageDB(Base):
    """
    This class defines the structure of the `chat_messages` table in the database, which stores
    all the messages exchanged during a chat session.

    Attributes:
    -----------
    id : int
        The primary key for each message, auto-incremented.
    user_id : int
        The ID of the user sending or receiving the message.
    session_id : str
        The unique session ID that ties together all messages in a conversation.
    sender : str
        Identifies whether the message was sent by the human user ('human') or the AI model ('ai').
    content : str
        The actual content of the message.
    timestamp : datetime
        The time when the message was sent, defaulting to the current UTC time.
    tone : str
        The tone of the message (e.g., friendly, professional). Optional.
    intent : str
        The intended meaning or purpose behind the message (if any). Optional.
    model : str
        The name of the model that generated the message (in the case of AI-generated messages). Optional.
    feedback : str
        Feedback from the user about the message, if any. Optional.
    language : str
        The language in which the message was written. Optional.
    message_type : str
        The type of the message, defaults to "text" but could be "file" or other formats. Optional.
    session_status : str
        Status of the session when the message was exchanged (e.g., "ongoing", "closed"). Defaults to "ongoing".
    """
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    session_id = Column(String, index=True)
    sender = Column(String, nullable=False)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tone = Column(String, nullable=True)
    intent = Column(String, nullable=True)
    model = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    language = Column(String, nullable=True)
    message_type = Column(String, default="text")
    session_status = Column(String, default="ongoing")


# Setup Database
engine = create_engine("sqlite:///database//chat_history.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define DB-backed Message History class
class DatabaseChatMessageHistory(BaseChatMessageHistory):
    """
    A class that manages the database-backed message history for each session.

    This class uses SQLAlchemy to interact with the database and stores chat messages in the `chat_messages` table.
    It also allows retrieving messages for a specific session and user.

    Attributes:
    -----------
    user_id : str
        The ID of the user for which the message history is being managed.
    session_id : str
        The session ID to identify the specific chat session.
    db_session : session
        The SQLAlchemy session for interacting with the database.

    Methods:
    --------
    add_message(message, tone=None, intent=None, model=None, feedback=None, language=None, message_type="text"):
        Adds a message to the chat history with additional metadata like tone, intent, and model used.

    get_messages():
        Retrieves all messages for the current session from the database.

    clear():
        Clears all chat history for the current user session.
    """

    def __init__(self, user_id: str, session_id: str):
        """
        Initialize the DatabaseChatMessageHistory class.

        Parameters:
        -----------
        user_id : str
            The ID of the user whose chat messages are being tracked.
        session_id : str
            The session ID associated with the conversation.
        """
        self.user_id = user_id
        self.session_id = session_id
        self.db_session = SessionLocal()

    def add_message(self, message: ChatMessage, tone=None, intent=None, model=None, feedback=None, language=None,
                    message_type="text") -> None:
        """
        Adds a new message to the chat history, saving it to the database with additional metadata.

        Parameters:
        -----------
        message : ChatMessage
            The message object (HumanMessage or AIMessage) to be added.
        tone : str, optional
            The tone of the message (e.g., friendly, professional).
        intent : str, optional
            The intent or purpose of the message.
        model : str, optional
            The name of the model used to generate the message.
        feedback : str, optional
            Feedback provided by the user about the message.
        language : str, optional
            The language in which the message is written.
        message_type : str, default="text"
            The type of message (e.g., "text", "file").
        """
        sender = "human" if isinstance(message, HumanMessage) else "ai"
        db_message = ChatMessageDB(
            user_id=self.user_id,
            session_id=self.session_id,
            sender=sender,
            content=message.content,
            tone=tone,
            intent=intent,
            model=model,
            feedback=feedback,
            language=language,
            message_type=message_type
        )
        self.db_session.add(db_message)
        self.db_session.commit()

    def get_messages(self) -> list[ChatMessage]:
        """
        Retrieves the chat history for the current session from the database.

        Returns:
        --------
        list[ChatMessage]
            A list of ChatMessage objects (HumanMessage or AIMessage) retrieved from the database.
        """
        db_messages = self.db_session.query(ChatMessageDB).filter_by(session_id=self.user_id).all()
        chat_messages = []
        for db_message in db_messages:
            if db_message.sender == "human":
                chat_messages.append(HumanMessage(content=db_message.content))
            else:
                chat_messages.append(AIMessage(content=db_message.content))
        return chat_messages

    def clear(self) -> None:
        """
        Deletes all messages for the current user session from the database.
        """
        self.db_session.query(ChatMessageDB).filter_by(user_id=self.user_id).delete()
        self.db_session.commit()
