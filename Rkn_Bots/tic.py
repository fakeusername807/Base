import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Starting the Tic-Tac-Toe game
@Client.on_message(filters.command("tic"))
async def start(client, message):
    chat_id = message.chat.id
    text = "Let's play Tic Tac Toe! You are X, and the bot is O."
    reset_board(chat_id)
    await send_game_board(client, chat_id)


# Reset the board for the given chat_id
def reset_board(chat_id):
    board = ["", "", "", "", "", "", "", "", ""]
    save_board(chat_id, board)


# Save the board state to a file
def save_board(chat_id, board):
    with open(f"board_{chat_id}.json", "w") as f:
        json.dump(board, f)


# Load the board state from a file
def load_board(chat_id):
    if os.path.exists(f"board_{chat_id}.json"):
        with open(f"board_{chat_id}.json", "r") as f:
            return json.load(f)
    else:
        return ["", "", "", "", "", "", "", "", ""]


# Send the Tic-Tac-Toe board as an inline keyboard
async def send_game_board(client, chat_id, message_id=None):
    board = load_board(chat_id)

    keyboard = [
        [
            InlineKeyboardButton(board[0] or ".", callback_data="0"),
            InlineKeyboardButton(board[1] or ".", callback_data="1"),
            InlineKeyboardButton(board[2] or ".", callback_data="2")
        ],
        [
            InlineKeyboardButton(board[3] or ".", callback_data="3"),
            InlineKeyboardButton(board[4] or ".", callback_data="4"),
            InlineKeyboardButton(board[5] or ".", callback_data="5")
        ],
        [
            InlineKeyboardButton(board[6] or ".", callback_data="6"),
            InlineKeyboardButton(board[7] or ".", callback_data="7"),
            InlineKeyboardButton(board[8] or ".", callback_data="8")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if message_id:
        await client.edit_message_text(chat_id=chat_id, message_id=message_id, text="Tic Tac Toe", reply_markup=reply_markup)
    else:
        await client.send_message(chat_id=chat_id, text="Tic Tac Toe", reply_markup=reply_markup)


# Handling the player's move
@Client.on_callback_query()
async def handle_move(client, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id
    callback_data = callback_query.data
    board = load_board(chat_id)

    if board[int(callback_data)] == "":
        board[int(callback_data)] = "X"

        if check_winner(board, "X"):
            await client.send_message(chat_id=chat_id, text="You win!")
            reset_board(chat_id)
            await send_game_board(client, chat_id, message_id)
            return

        if is_board_full(board):
            await client.send_message(chat_id=chat_id, text="It's a draw!")
            reset_board(chat_id)
            await send_game_board(client, chat_id, message_id)
            return

        board = bot_move(board)

        if check_winner(board, "O"):
            await client.send_message(chat_id=chat_id, text="The bot wins!")
            reset_board(chat_id)
            await send_game_board(client, chat_id, message_id)
            return

        if is_board_full(board):
            await client.send_message(chat_id=chat_id, text="It's a draw!")
            reset_board(chat_id)
            await send_game_board(client, chat_id, message_id)
            return

        save_board(chat_id, board)
        await send_game_board(client, chat_id, message_id)


# Bot's move logic
def bot_move(board):
    winning_move = find_winning_move(board, "O")
    if winning_move is not None:
        board[winning_move] = "O"
        return board

    blocking_move = find_winning_move(board, "X")
    if blocking_move is not None:
        board[blocking_move] = "O"
        return board

    if board[4] == "":
        board[4] = "O"
        return board

    corners = [0, 2, 6, 8]
    for corner in corners:
        if board[corner] == "":
            board[corner] = "O"
            return board

    sides = [1, 3, 5, 7]
    for side in sides:
        if board[side] == "":
            board[side] = "O"
            return board

    return board


# Finding a winning move
def find_winning_move(board, player):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    for combo in winning_combinations:
        player_count = sum(1 for i in combo if board[i] == player)
        empty_index = next((i for i in combo if board[i] == ""), None)
        if player_count == 2 and empty_index is not None:
            return empty_index

    return None


# Check if a player has won
def check_winner(board, player):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    return any(all(board[i] == player for i in combo) for combo in winning_combinations)


# Check if the board is full
def is_board_full(board):
    return all(cell != "" for cell in board)
