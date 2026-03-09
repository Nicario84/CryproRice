// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract PrivateVoting {

    struct Candidate {
        string name;
        uint256 voteCount;
    }

    address public authority;
    string public electionTitle;

    uint256 public votingStart;
    uint256 public votingEnd;

    bool public requireApproval;   // NEW TOGGLE
    bool public resultsPublished;

    Candidate[] private candidates;

    mapping(address => bool) public isApprovedVoter;
    mapping(address => bool) public hasVoted;
    mapping(address => bytes) public encryptedBallot;

    address[] private voterList;

    event ElectionCreated(string title, uint256 start, uint256 end);
    event VoterApproved(address voter);
    event BallotSubmitted(address indexed voter);
    event ResultsPublished(uint256 timestamp);

    modifier onlyAuthority() {
        require(msg.sender == authority, "Only authority can call this");
        _;
    }

    modifier duringVoting() {
        require(block.timestamp >= votingStart, "Voting has not started yet");
        require(block.timestamp <= votingEnd, "Voting period has ended");
        _;
    }

    modifier afterVoting() {
        require(block.timestamp > votingEnd, "Voting period not over yet");
        _;
    }

    constructor(
        string memory _title,
        string[] memory _candidateNames,
        uint256 _durationSeconds,
        bool _requireApproval     // NEW PARAMETER
    ) {
        require(bytes(_title).length > 0, "Election title required");
        require(_durationSeconds > 0, "Duration must be greater than 0");
        require(_candidateNames.length > 1, "Need at least 2 candidates");

        authority = msg.sender;
        electionTitle = _title;

        votingStart = block.timestamp;
        votingEnd = block.timestamp + _durationSeconds;

        requireApproval = _requireApproval;   // SET MODE

        for (uint256 i = 0; i < _candidateNames.length; i++) {
            candidates.push(
                Candidate({
                    name: _candidateNames[i],
                    voteCount: 0
                })
            );
        }

        emit ElectionCreated(_title, votingStart, votingEnd);
    }

    function approveVoter(address voter) external onlyAuthority {
        require(voter != address(0), "Invalid address");
        require(!isApprovedVoter[voter], "Voter already approved");

        isApprovedVoter[voter] = true;
        emit VoterApproved(voter);
    }

    function approveManyVoters(address[] calldata voters) external onlyAuthority {
        for (uint256 i = 0; i < voters.length; i++) {
            address voter = voters[i];

            if (voter != address(0) && !isApprovedVoter[voter]) {
                isApprovedVoter[voter] = true;
                emit VoterApproved(voter);
            }
        }
    }

    function vote(bytes calldata _encryptedVote) external duringVoting {

        // TOGGLE CHECK
        if (requireApproval) {
            require(isApprovedVoter[msg.sender], "You are not an approved voter");
        }

        require(!hasVoted[msg.sender], "You have already voted");
        require(_encryptedVote.length > 0, "Encrypted ballot cannot be empty");

        hasVoted[msg.sender] = true;
        encryptedBallot[msg.sender] = _encryptedVote;

        voterList.push(msg.sender);

        emit BallotSubmitted(msg.sender);
    }

    function publishFinalResults(uint256[] calldata counts)
        external
        onlyAuthority
        afterVoting
    {
        require(!resultsPublished, "Results already published");
        require(counts.length == candidates.length, "Counts must match candidates");

        uint256 totalCounted = 0;

        for (uint256 i = 0; i < counts.length; i++) {
            totalCounted += counts[i];
        }

        require(totalCounted <= voterList.length, "More votes than voters");

        for (uint256 i = 0; i < counts.length; i++) {
            candidates[i].voteCount = counts[i];
        }

        resultsPublished = true;

        emit ResultsPublished(block.timestamp);
    }

    function getCandidates() external view returns (Candidate[] memory) {
        return candidates;
    }

    function getCandidateCount() external view returns (uint256) {
        return candidates.length;
    }

    function getVoterList() external view returns (address[] memory) {
        return voterList;
    }

    function getElectionStatus() external view returns (string memory) {
        if (block.timestamp < votingStart) return "Setup";
        if (block.timestamp <= votingEnd) return "Voting";
        if (!resultsPublished) return "Awaiting results";
        return "Closed";
    }

    function timeRemaining() external view returns (uint256) {
        if (block.timestamp >= votingEnd) return 0;
        return votingEnd - block.timestamp;
    }

    function getWinner() external view returns (string memory) {
        require(resultsPublished, "Results not published yet");

        uint256 winnerIndex = 0;
        uint256 maxVotes = candidates[0].voteCount;

        for (uint256 i = 1; i < candidates.length; i++) {
            if (candidates[i].voteCount > maxVotes) {
                maxVotes = candidates[i].voteCount;
                winnerIndex = i;
            }
        }

        return candidates[winnerIndex].name;
    }
}