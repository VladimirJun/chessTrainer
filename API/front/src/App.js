import React, { useState } from "react";
import axios from "axios";
import Chessboard from "chessboardjsx";
import { Chess } from "chess.js";
import "./App.css";

const API_URL = "http://localhost:8001/api";

const App = () => {
    const [gameId, setGameId] = useState(null);
    const [playerId, setPlayerId] = useState("");
    const [playerColor, setPlayerColor] = useState("white");
    const [fen, setFen] = useState("start");
    const [engineRating, setEngineRating] = useState(null);
    const [playerRating, setPlayerRating] = useState(null);
    const [evaluation, setEvaluation] = useState(null);  // ➕ Храним total_evaluation
    const [feedbackMessage, setFeedbackMessage] = useState(null);  // ➕ Храним сообщение

    const fetchPlayerRating = async (id) => {
        try {
            const response = await axios.get(`${API_URL}/player/${id}`);
            return response.data.rating;
        } catch (error) {
            console.error("Error fetching player rating:", error);
            alert("Failed to fetch player rating. Check console for details.");
            return null;
        }
    };

    const handleCreateGame = async () => {
        if (!playerId) {
            alert("Player ID is required.");
            return;
        }

        try {
            const rating = await fetchPlayerRating(playerId);
            if (rating !== null) {
                setPlayerRating(rating);
            }

            const response = await axios.post(`${API_URL}/match`, {
                id: 1,
                player_id: playerId,
                moves: "",
                player_color: playerColor,
            });
            setGameId(response.data.id);

            if (playerColor === "black" && response.data.moves) {
                const chess = new Chess();
                const moveList = response.data.moves
                    .split(/\s+/)
                    .filter((item) => !item.includes("."));

                moveList.forEach((move) => {
                    chess.move(move);
                });

                setFen(chess.fen());
            } else {
                setFen("start");
            }

            alert(`Game created with ID: ${response.data.id}`);
        } catch (error) {
            console.error("Error creating game:", error);
            alert("Failed to create game. Check console for details.");
        }
    };

    const handleMove = async (move) => {
        try {
            const response = await axios.post(`${API_URL}/match/${gameId}/move`, {
                move: move,
            });

            setFen(response.data.fen);
            setEngineRating(response.data.engine_rating);
            setPlayerRating(response.data.new_player_rating);
            setEvaluation(response.data.evaluation_after.total_evaluation);  // ➕ Обновляем total_evaluation
            setFeedbackMessage(response.data.feedback_messages[0] || null);  // ➕ Обновляем сообщение об ухудшении
        } catch (error) {
            console.error("Error making move:", error);
            alert("Failed to make move. Check console for details.");
        }
    };

    const handleFinishGame = async () => {
        try {
            await axios.post(`${API_URL}/match/${gameId}/finish`);
            alert("Game finished.");
            setGameId(null);
            setFen("start");
            setEngineRating(null);
            setPlayerRating(null);
            setEvaluation(null);  // ➕ Обнуляем оценку
            setFeedbackMessage(null);  // ➕ Обнуляем сообщение
        } catch (error) {
            console.error("Error finishing game:", error);
            alert("Failed to finish game. Check console for details.");
        }
    };

    return (
        <div className="app-container">
            <h1 className="app-title">ChessTrainerTester</h1>
            <div className="form-container">
                <label className="form-label">
                    Player ID:
                    <input
                        type="text"
                        value={playerId}
                        onChange={(e) => setPlayerId(e.target.value)}
                        placeholder="Enter Player ID"
                        className="form-input"
                    />
                </label>
                <label className="form-label">
                    Player Color:
                    <select
                        value={playerColor}
                        onChange={(e) => setPlayerColor(e.target.value)}
                        className="form-select"
                    >
                        <option value="white">White</option>
                        <option value="black">Black</option>
                    </select>
                </label>
                <button className="form-button" onClick={handleCreateGame}>
                    Create Game
                </button>
            </div>
            {gameId && (
                <div className="game-container">
                    <h2>Game ID: {gameId}</h2>
                    <h3>Player Rating: {playerRating || "Unknown"}</h3>
                    <h3>Engine Rating: {engineRating || "Unknown"}</h3>
{feedbackMessage && <h3 className="feedback">{feedbackMessage}</h3>}


                    <div className="chessboard-container">
                        <Chessboard
                            position={fen}
                            onDrop={(move) => {
                                const from = move.sourceSquare;
                                const to = move.targetSquare;
                                const promotion =
                                    move.piece[1] === "p" &&
                                    (to[1] === "8" || to[1] === "1")
                                        ? "q"
                                        : "";
                                handleMove(`${from}${to}${promotion}`);
                            }}
                            orientation={playerColor}
                        />
                    </div>
                    <button className="form-button finish-button" onClick={handleFinishGame}>
                        Finish Game
                    </button>
                </div>
            )}
        </div>
    );
};

export default App;
