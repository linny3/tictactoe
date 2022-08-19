from re import X
from flask import Flask ,render_template, session, redirect, url_for, flash
from flask_session import Session
from tempfile import mkdtemp
import math
from sqlalchemy import true
import copy

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

moves = []

@app.route("/")
def index():
    # if board doesnt exist
    if "board" not in session:
        session["board"] = [[None, None, None], [None, None, None,], [None, None, None]]
        session["turn"] = "X"
    # call winner function to see if anyone has won yet
    winners = winner(session["board"])
    # return game.html with board, turn, moves and winner variables
    return render_template("game.html", game=session["board"], turn=session["turn"], winner=winners, move=moves)
    

@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    # play move on board where current user turn clicked. 
    session["board"][row][col] = session["turn"]
    # store board with new move made in board history
    move = session["board"]
    # move turn to next user 
    if session["turn"] == "X":
        session["turn"] = "O"
    else:
        session["turn"] = "X"
    # add move that was made to moves list
    moves.append(move)
    # store in session moves list
    session["move"] = moves
    # return index
    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    # reset board back to none when reset link clicked
    # clear all sessions
    session.clear()
    # clear moves list
    moves.clear()
    # return to index
    return redirect(url_for("index"))


# Check to see if anyone has won the game yet
@app.route("/winner")
def winner(board):
    # intitialize x and o
    x = 0
    o = 0
    session.pop('_flashes', None)
    
   # loop through board checking if row has 'X' or '0' 3 times in a row
    for row in board:
        for col in row:
            # if current square has 'X'
            if col == "X":
                # add 1 to x
                x = x + 1
                # reset o to zero
                o = 0
            # if current square has '0'    
            elif col == "O":
                # reset 'X' to zero
                x = 0
                # add 1 to o
                o = o + 1
            # if current square is none
            else:
                # reset both variables back to zero
                x = 0
                o = 0
                
        # if x count equals 3        
        if x == 3:
            # flash message for winner 'X'
            flash("Winner is X!")
            return 1
        # if o count equals 3    
        elif o == 3:
            # flash message for winner 'O'
            flash("Winner is O!")
            o = 0
            return -1
        # set x and o to zero
        x = 0 
        o = 0     
    # check if column is winner 
    for i in range(3):
        #  loop through board checking columns
        new_board = ([col[i] for col in board])
        for row in new_board:
                # if column square is 'X'
                if row == "X":
                    # add 1 to x
                    x = x + 1
                    o = 0
                # if column square is 'O'
                elif row == "O":
                    x = 0
                    # add 1 to o
                    o = o + 1

                else:
                    # if square is none set both variables back to zero
                    x = 0
                    o = 0
                # if x equals 3 than there is a winner
                if x == 3:
                    # flash winner 'X'
                    flash("Winner is X!")
                    return 1
                # if o equals 3 than winner is 'O'
                elif o == 3:
                    # flash winner is 'O'
                    flash("Winner is O!")
                    return -1
        x = 0 
        o = 0       
    # check diagonal for winner
    for i in range(3):
            # if diagonal square is equal to 'X'
            if board[i][i] == "X":
                # add 1 to x
                x = x + 1
            # if diagonal square is equal to 'O'
            elif board[i][i] == "O":
                # add 1 to o
                o = o + 1 
            # if diagonal square is none
            else:
                x = 0
                o = 0
            # if x is equal to 3 than winner is X
            if x == 3:
                # flash winner X
                flash("Winner is X!")
                return 1
            # if winner is o
            if o == 3:
                # flash winner
                flash("Winner is O!")
                return -1    
    x = 0
    o = 0
    # check diagonal top left to bottom right
    for i in range(3):
        # if current square is 'X'
        if board[i][3 - i - 1] == "X":
            # add 1 to x
            x = x + 1
        # if current square is 'O'
        elif board[i][3 - i - 1] == "O":
            # add 1 to o
            o = o + 1
        # if current square is none
        else:
            x = 0
            o = 0    
        # if x equals 3 then winner is 'X'
        if x == 3:
            # flash winner X
            flash("Winner is X!")
            return 1
        # if x equals 3 then winner is 'O'
        if o == 3:
            # flash message O
            flash("Winner is O!")
            return -1
    if len(moves) == 9:
        flash("Tie Game!")
    x = 0
    o = 0
    # if no winner yet return false
    return 0

# Undo previouse move when undo link clicked    
@app.route("/undo")
def undo():
    # if only one move has been made and undo is clicked
    if len(moves) <= 1:
        # reset board
        reset()
        # delete move from moves list
        del moves[:]
    
    # if more than one move has been made
    else:
        # remove the last set of moves in moves list
        moves.remove(moves[-1])
        # set current board to new last move in list
        session["board"] = moves[-1]
        # set the correct persons turn
        if session["turn"] == "X":
            session["turn"] = "O"
        else:
            session["turn"] = "X"

    
    # clear messages if any are popped up    
    session.pop('_flashes', None)
    # return index
    return redirect(url_for("index"))

# let computer make move for you
@app.route("/computer")
def computer():
    # current turn 
    turn = session["turn"]
    # current game board
    game = session["board"]
    # set best value so that you can sort the returning values from minimax
    bestX = -1000
    # set bestval to high number
    bestO = 1000
    # set the best move to off board and change once bestVal has been set
    bestMove = (-1, -1)
    # keep count to see if board is all None
    nonecount = 0

    for i in range(3):
        for j in range(3):
            if game[i][j] == None:
                nonecount = nonecount + 1

    if nonecount == 9:
        play(0,0)
        return redirect(url_for("index")) 

    # loop through board
    for i in range(3):
        for j in range(3):
            # if spot is empty add current players turn
            if game[i][j] == None:
                game[i][j] = turn
                # if current player is X return minimax with O as turn
                if turn == "X":
                    turn = "O"
                    # calculate moveVal by calling minimax
                    moveVal = minimax(game, turn)
                    # return turn back to X
                    turn = "X"
                # if current player is O return minimax with X as turn
                else:
                    turn = "X"
                    # calculate moveVal by calling minimax
                    moveVal = minimax(game, turn)
                    # return turn back O
                    turn = "O"
                # undo move that was made   
                game[i][j] = None

                
                # if X's turn return the highest valued move
                if turn == "X":
                    # if current move value is greater than bestVal 
                    if moveVal > bestX:
                        # current i, j (board  position) is bestMove
                        bestMove = (i, j)
                        # change best value to current value
                        bestX = moveVal
                # if O's turn return the lowest value
                else:
                    # if current move is less than bestval
                    if moveVal < bestO:
                        # change best move to current i, j
                        bestMove = (i, j)
                        # change best value to current value
                        bestO = moveVal
    
    # call the play function with best moves           
    play(bestMove[0],bestMove[1])
    return redirect(url_for("index"))

# a.i algorithim 
def minimax(game, turn):
    # call winner function to see if current board is winner
    won = winner(game)
    # empty list to store possible moves
    moves = []
    # if X is the winner
    if won == 1:
        # return 1
        value = 1
        return value
    # if O is the winner
    elif won == -1:
        # return -1
        value = -1
        return value
    
    # loop through board checking for unplayed spots
    for i in range(3):
        for j in range(3):
            if game[i][j] == None:
                # add unplayed spots to moves list
                moves.append([i,j])  
    # if no spots are unplayed and no one is winner the game must be tied
    if len(moves) == 0:
        return 0
    
    # if current turn is X
    if turn == "X":
        # set value low because we want to maximize it
        value = -1000
        # loop through list of possible moves
        for move in moves:
            # change spot on the board to current turn
            game[move[0]][move[1]] = "X"
            # recursivly call the minimax function with O's turn
            value = max(value, minimax(game, "O"))
            # revert board back to before function call 
            game[move[0]][move[1]] = None
        # return the value
        return value
    # else if O's turn
    elif turn == "O":
        # set value high
        value = 1000
        #loop through board
        for move in moves:
            # change unplayed move to O
            game[move[0]][move[1]] = "O"
            # recursively call minimax with X as turn 
            value = min(value, minimax(game, "X"))
            # revert board to before function call
            game[move[0]][move[1]] = None
        # return the value 
        return value