
contract TournamentManager {
    mapping(string => string) public tournamentScores;
    address public owner;

    constructor() public {
        owner = msg.sender;
    }

    function setScore(string memory matchId, string memory score) public {
        tournamentScores[matchId] = score;
    }

    function getScore(string memory matchId) view public returns (string memory) {
            return tournamentScores[matchId];
    }

    function THEnumber() view public returns (uint) {
        return 42;
    }

    function destroy() public {
        require(msg.sender == owner, "msg.sender is not the owner");
        selfdestruct(payable(owner));
    }
} 