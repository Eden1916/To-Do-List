Chat-Based To-Do List API

This project is a high-performance backend API for managing a user's to-do list through a conversational interface, built using FastAPI, SQLAlchemy, and Pydantic.
The primary goal is to create a REST API that supports conversational input for managing tasks. 
Instead of using traditional forms, users interact with the API by sending simple text commands (e.g., "add study session," "mark task 5 as done").
The system uses a dedicated sessions table to maintain the state and context of the conversation.