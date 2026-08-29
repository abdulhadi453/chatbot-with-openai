"""
Agent service using OpenAI Chat Completions API.
Handles AI agent initialization, conversation execution, and response generation.
Includes real-time web search capabilities for current information.
"""
import logging
import json
from typing import Optional, AsyncGenerator, List, Dict
from datetime import datetime, UTC
from openai import AsyncOpenAI
from app.config.settings import settings
from app.utils.web_search import search_web, get_current_datetime

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing OpenAI Chat Completions interactions with web search."""

    def __init__(self):
        """Initialize the agent service with OpenAI client and tools."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Enhanced system message with web search capability
        current_date = datetime.now(UTC).strftime("%B %d, %Y")
        self.system_message = {
            "role": "system",
            "content": f"""{settings.AGENT_INSTRUCTIONS}

LANGUAGE CONSISTENCY RULES (CRITICAL):
1. ALWAYS respond in the SAME language the user is using
2. Detect the user's language from their message
3. Maintain consistent language throughout your entire response
4. DO NOT mix languages in a single response
5. For Hindi/Urdu:
   - If user writes in Hindi (Devanagari script), respond ONLY in Hindi
   - If user writes in Urdu (Arabic script), respond ONLY in Urdu
   - If user writes in Roman Urdu/Hindi, match their romanization style
   - DO NOT mix Hindi and Urdu vocabulary in the same response
6. For English, respond in clear, natural English
7. For any other language, respond entirely in that language
8. If user switches languages, switch your response language accordingly

Examples:
- User writes in English → Respond in English
- User writes in Hindi → Respond completely in Hindi (Devanagari)
- User writes in Urdu → Respond completely in Urdu (Arabic script)
- User writes in Spanish → Respond completely in Spanish

IMPORTANT: You have access to real-time web search capabilities. Use them when:
- User asks about CURRENT, LATEST, RECENT, or LIVE information
- User asks "what is today", "current date", "what time is it"
- User asks about NEWS, EVENTS happening NOW or RECENTLY
- User asks about STOCK PRICES, WEATHER, SPORTS SCORES, POLITICAL POSITIONS
- User asks about any information that changes over time
- User explicitly requests "search", "look up", "find"

Current date: {current_date}

CRITICAL: When you receive search results:
1. READ the search results carefully - they contain current, accurate information
2. Base your answer on the search results, NOT on your training data
3. Synthesize information from multiple search results when available
4. ALWAYS mention that the information is current/up-to-date (e.g., "As of {current_date}...")
5. If search results are unclear or contradictory, acknowledge this in your response
6. RESPOND IN THE SAME LANGUAGE AS THE USER'S QUERY

For queries that don't require current information (like general knowledge, definitions, explanations of concepts), answer directly without searching - but ALWAYS in the user's language."""
        }

        # Define available tools/functions
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for current, up-to-date information. Use this when the user asks about recent events, current data, news, or anything that requires real-time information. Returns search results with titles, snippets, and URLs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query. Be specific and include relevant keywords."
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of search results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_datetime",
                    "description": "Get the current date and time. Use this when the user asks 'what is today', 'what time is it', 'current date', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

        # In-memory conversation history storage
        self._conversation_histories: Dict[str, List[Dict]] = {}

        logger.info(f"Agent initialized with model {settings.AGENT_MODEL} and web search capabilities")

    def _get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Get conversation history for a given conversation.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            List of message dictionaries
        """
        if conversation_id not in self._conversation_histories:
            self._conversation_histories[conversation_id] = []
        return self._conversation_histories[conversation_id]

    def _add_to_history(self, conversation_id: str, role: str, content: str):
        """
        Add a message to conversation history.

        Args:
            conversation_id: Unique identifier for the conversation
            role: Message role (user/assistant)
            content: Message content
        """
        history = self._get_conversation_history(conversation_id)
        history.append({"role": role, "content": content})

        # Keep only last 20 messages to manage context window
        if len(history) > 20:
            self._conversation_histories[conversation_id] = history[-20:]

    async def _execute_function(self, function_name: str, arguments: Dict) -> str:
        """
        Execute a function call from the AI.

        Args:
            function_name: Name of the function to execute
            arguments: Function arguments as dictionary

        Returns:
            JSON string with function results
        """
        try:
            if function_name == "search_web":
                query = arguments.get("query", "")
                max_results = arguments.get("max_results", 5)
                result = await search_web(query, max_results)
                return json.dumps(result)

            elif function_name == "get_current_datetime":
                result = get_current_datetime()
                return json.dumps(result)

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                })

        except Exception as e:
            logger.error(f"Function execution error: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    async def generate_response(
        self,
        conversation_id: str,
        user_message: str
    ) -> str:
        """
        Generate AI response for a user message with web search support.
        Maintains conversation history automatically.

        Args:
            conversation_id: Unique identifier for the conversation
            user_message: The user's input message

        Returns:
            The assistant's response text
        """
        try:
            # Add user message to history
            self._add_to_history(conversation_id, "user", user_message)

            # Get conversation history
            history = self._get_conversation_history(conversation_id)

            # Build messages for API call
            messages = [self.system_message] + history

            # Initial API call with tools
            response = await self.client.chat.completions.create(
                model=settings.AGENT_MODEL,
                messages=messages,
                temperature=settings.AGENT_TEMPERATURE,
                max_tokens=settings.AGENT_MAX_TOKENS,
                tools=self.tools,
                tool_choice="auto"  # Let AI decide when to use tools
            )

            # Process response - handle function calls
            assistant_message = response.choices[0].message

            # Check if AI wants to call a function
            if assistant_message.tool_calls:
                logger.info(f"AI requested function calls: {len(assistant_message.tool_calls)}")

                # Add assistant's function call to messages
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in assistant_message.tool_calls
                    ]
                })

                # Execute each function call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Executing function: {function_name} with args: {function_args}")

                    # Execute the function
                    function_result = await self._execute_function(function_name, function_args)

                    # Add function result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_result
                    })

                # Get final response from AI with function results
                final_response = await self.client.chat.completions.create(
                    model=settings.AGENT_MODEL,
                    messages=messages,
                    temperature=settings.AGENT_TEMPERATURE,
                    max_tokens=settings.AGENT_MAX_TOKENS
                )

                assistant_text = final_response.choices[0].message.content

                logger.info(
                    f"Generated response with {len(assistant_message.tool_calls)} function calls "
                    f"(tokens: {final_response.usage.total_tokens})"
                )
            else:
                # No function calls, use direct response
                assistant_text = assistant_message.content

                logger.info(
                    f"Generated response for conversation {conversation_id} "
                    f"(tokens: {response.usage.total_tokens})"
                )

            # Add assistant response to history
            self._add_to_history(conversation_id, "assistant", assistant_text)

            return assistant_text

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise Exception(f"Failed to generate AI response: {str(e)}")

    async def generate_response_streamed(
        self,
        conversation_id: str,
        user_message: str
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming AI response for real-time updates with web search support.

        Args:
            conversation_id: Unique identifier for the conversation
            user_message: The user's input message

        Yields:
            Text chunks as they are generated
        """
        try:
            # Add user message to history
            self._add_to_history(conversation_id, "user", user_message)

            # Get conversation history
            history = self._get_conversation_history(conversation_id)

            # Build messages for API call
            messages = [self.system_message] + history

            # First, check if AI needs to call functions (non-streaming check)
            initial_response = await self.client.chat.completions.create(
                model=settings.AGENT_MODEL,
                messages=messages,
                temperature=settings.AGENT_TEMPERATURE,
                max_tokens=settings.AGENT_MAX_TOKENS,
                tools=self.tools,
                tool_choice="auto"
            )

            assistant_message = initial_response.choices[0].message

            # If AI wants to call functions, execute them first
            if assistant_message.tool_calls:
                logger.info(f"Streaming: AI requested {len(assistant_message.tool_calls)} function calls")

                # Add assistant's function call to messages
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in assistant_message.tool_calls
                    ]
                })

                # Execute each function call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Streaming: Executing {function_name} with args: {function_args}")

                    # Yield a status message about the search
                    if function_name == "search_web":
                        yield f"[Searching the web for: {function_args.get('query', 'information')}...]\n\n"

                    # Execute the function
                    function_result = await self._execute_function(function_name, function_args)

                    # Add function result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_result
                    })

                # Now stream the final response with function results
                stream = await self.client.chat.completions.create(
                    model=settings.AGENT_MODEL,
                    messages=messages,
                    temperature=settings.AGENT_TEMPERATURE,
                    max_tokens=settings.AGENT_MAX_TOKENS,
                    stream=True
                )
            else:
                # No function calls needed, stream directly
                stream = await self.client.chat.completions.create(
                    model=settings.AGENT_MODEL,
                    messages=messages,
                    temperature=settings.AGENT_TEMPERATURE,
                    max_tokens=settings.AGENT_MAX_TOKENS,
                    stream=True
                )

            # Collect full response for history
            full_response = ""

            # Stream chunks
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # Add complete assistant response to history
            self._add_to_history(conversation_id, "assistant", full_response)

            logger.info(f"Completed streaming response for conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise Exception(f"Failed to stream AI response: {str(e)}")

    def clear_conversation_history(self, conversation_id: str):
        """
        Clear conversation history for a given conversation.

        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id in self._conversation_histories:
            del self._conversation_histories[conversation_id]
            logger.info(f"Cleared history for conversation {conversation_id}")

    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """
        Get all messages in a conversation.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            List of message dictionaries
        """
        return self._get_conversation_history(conversation_id).copy()


# Global agent service instance
agent_service = AgentService()
