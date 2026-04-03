// NBA Z-LOCK - Frontend JavaScript

let teams = [];
let modelStatus = null;

// Track player status and probability for injury management
// Structure: { teamType: { playerName: { status: 'out'|'questionable'|'available', probability: 0.0-1.0 } } }
let playerStatuses = {
    home: {},
    visitor: {}
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTeams();
    checkModelStatus();
    setupEventListeners();
});

let homeRoster = [];
let visitorRoster = [];

function setupEventListeners() {
    const homeSelect = document.getElementById('home-team');
    const visitorSelect = document.getElementById('visitor-team');
    const predictBtn = document.getElementById('predict-btn');
    const clearInjuriesBtn = document.getElementById('clear-injuries-btn');
    const homeInjuredSelect = document.getElementById('home-injured-players');
    const visitorInjuredSelect = document.getElementById('visitor-injured-players');
    const clearHomeInjuriesBtn = document.getElementById('clear-home-injuries-btn');
    const clearVisitorInjuriesBtn = document.getElementById('clear-visitor-injuries-btn');
    const noHomeInjuriesBtn = document.getElementById('no-home-injuries-btn');
    const noVisitorInjuriesBtn = document.getElementById('no-visitor-injuries-btn');
    
    // Load roster when home team is selected
    homeSelect.addEventListener('change', function() {
        const bothSelected = homeSelect.value && visitorSelect.value;
        const differentTeams = homeSelect.value !== visitorSelect.value;
        predictBtn.disabled = !(bothSelected && differentTeams);
        
        if (homeSelect.value) {
            loadTeamRoster(parseInt(homeSelect.value), 'home');
        } else {
            clearRoster('home');
        }
    });
    
    // Load roster when visitor team is selected
    visitorSelect.addEventListener('change', function() {
        const bothSelected = homeSelect.value && visitorSelect.value;
        const differentTeams = homeSelect.value !== visitorSelect.value;
        predictBtn.disabled = !(bothSelected && differentTeams);
        
        if (visitorSelect.value) {
            loadTeamRoster(parseInt(visitorSelect.value), 'visitor');
        } else {
            clearRoster('visitor');
        }
    });
    
    // Update selected count when players are selected
    if (homeInjuredSelect) {
        homeInjuredSelect.addEventListener('change', function() {
            updateSelectedCount('home');
            console.log('Home team injury selection changed');
        });
        
        // Also listen for click events to ensure multi-select works
        homeInjuredSelect.addEventListener('click', function() {
            // Small delay to allow selection to update
            setTimeout(() => updateSelectedCount('home'), 10);
        });
    }
    
    if (visitorInjuredSelect) {
        visitorInjuredSelect.addEventListener('change', function() {
            updateSelectedCount('visitor');
            console.log('Visitor team injury selection changed');
        });
        
        // Also listen for click events to ensure multi-select works
        visitorInjuredSelect.addEventListener('click', function() {
            // Small delay to allow selection to update
            setTimeout(() => updateSelectedCount('visitor'), 10);
        });
    }
    
    // Predict button click
    predictBtn.addEventListener('click', function() {
        makePrediction();
    });
    
    // Clear all injuries button
    if (clearInjuriesBtn) {
        clearInjuriesBtn.addEventListener('click', function() {
            clearInjuries();
        });
    }
    
    // Clear individual team injuries
    if (clearHomeInjuriesBtn) {
        clearHomeInjuriesBtn.addEventListener('click', function() {
            clearTeamInjuries('home');
        });
    }
    
    if (clearVisitorInjuriesBtn) {
        clearVisitorInjuriesBtn.addEventListener('click', function() {
            clearTeamInjuries('visitor');
        });
    }
    
    // No injuries buttons
    if (noHomeInjuriesBtn) {
        noHomeInjuriesBtn.addEventListener('click', function() {
            markNoInjuries('home');
        });
    }
    
    if (noVisitorInjuriesBtn) {
        noVisitorInjuriesBtn.addEventListener('click', function() {
            markNoInjuries('visitor');
        });
    }
}

async function loadTeams() {
    try {
        const response = await fetch('/api/teams');
        const data = await response.json();
        
        if (data.success) {
            teams = data.teams;
            populateTeamSelects();
        } else {
            showError('Failed to load teams: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        showError('Error loading teams: ' + error.message);
    }
}

function populateTeamSelects() {
    const homeSelect = document.getElementById('home-team');
    const visitorSelect = document.getElementById('visitor-team');
    
    // Clear existing options (except first)
    [homeSelect, visitorSelect].forEach(select => {
        while (select.options.length > 1) {
            select.remove(1);
        }
    });
    
    // Add teams
    teams.forEach(team => {
        const option1 = new Option(team.full_name, team.id);
        const option2 = new Option(team.full_name, team.id);
        homeSelect.add(option1);
        visitorSelect.add(option2);
    });
}

async function checkModelStatus() {
    try {
        const response = await fetch('/api/model/status');
        modelStatus = await response.json();
        
        const statusDiv = document.getElementById('model-status');
        if (modelStatus.trained) {
            statusDiv.className = 'model-status trained';
            const accuracy = modelStatus.training_results?.test_accuracy || 'N/A';
            statusDiv.innerHTML = `
                <p>✓ Model Trained</p>
                ${modelStatus.training_results ? 
                    `<p style="margin-top: 10px; font-size: 0.9rem;">Accuracy: ${(accuracy * 100).toFixed(1)}%</p>` : 
                    ''}
            `;
        } else {
            statusDiv.className = 'model-status not-trained';
            statusDiv.innerHTML = `
                <p>⚠ Model Not Trained</p>
                <p style="margin-top: 10px; font-size: 0.9rem;">
                    Please train the model first by running:<br>
                    <code>python models/train_model.py</code>
                </p>
            `;
        }
    } catch (error) {
        console.error('Error checking model status:', error);
    }
}

async function loadTeamRoster(teamId, teamType) {
    const selectElement = document.getElementById(`${teamType}-injured-players`);
    if (!selectElement) return;
    
    // Show loading
    selectElement.innerHTML = '<option disabled>Loading players...</option>';
    
    try {
        const response = await fetch(`/api/roster/${teamId}`);
        const data = await response.json();
        
        if (data.success && data.players) {
            // Store roster
            if (teamType === 'home') {
                homeRoster = data.players;
            } else {
                visitorRoster = data.players;
            }
            
            // Clear and populate dropdown
            selectElement.innerHTML = '';
            
            // Sort players: star first, then key, then role
            const sortedPlayers = [...data.players].sort((a, b) => {
                const typeOrder = { 'star': 0, 'key': 1, 'role': 2 };
                return typeOrder[a.type] - typeOrder[b.type];
            });
            
            sortedPlayers.forEach(player => {
                const option = document.createElement('option');
                option.value = player.name;
                option.textContent = `${player.name} (${player.position})`;
                option.setAttribute('data-type', player.type);
                // Add visual indicator for player type
                if (player.type === 'star') {
                    option.textContent = `⭐ ${player.name} (${player.position})`;
                } else if (player.type === 'key') {
                    option.textContent = `🔑 ${player.name} (${player.position})`;
                }
                selectElement.appendChild(option);
            });
            
            // Reset selection count after loading
            updateSelectedCount(teamType);
            
            // Add placeholder if no players
            if (sortedPlayers.length === 0) {
                selectElement.innerHTML = '<option disabled>No players found</option>';
            }
        } else {
            selectElement.innerHTML = '<option disabled>Error loading players</option>';
        }
    } catch (error) {
        console.error(`Error loading ${teamType} roster:`, error);
        selectElement.innerHTML = '<option disabled>Error loading players</option>';
    }
}

function clearRoster(teamType) {
    const selectElement = document.getElementById(`${teamType}-injured-players`);
    if (selectElement) {
        selectElement.innerHTML = '<option disabled>Select team first</option>';
    }
    if (teamType === 'home') {
        homeRoster = [];
    } else {
        visitorRoster = [];
    }
    updateSelectedCount(teamType);
}

function updateSelectedCount(teamType) {
    const selectElement = document.getElementById(`${teamType}-injured-players`);
    const countElement = document.getElementById(`${teamType}-selected-count`);
    
    if (!selectElement || !countElement) return;
    
    // Get selected options (excluding disabled ones)
    const selected = Array.from(selectElement.selectedOptions)
        .filter(opt => !opt.disabled && opt.value && opt.value.trim() !== '');
    const count = selected.length;
    const selectedPlayerNames = selected.map(opt => opt.value).filter(name => name && name.trim() !== '');
    
    // Update player statuses - remove players that are no longer selected
    const currentStatuses = playerStatuses[teamType];
    Object.keys(currentStatuses).forEach(playerName => {
        if (!selectedPlayerNames.includes(playerName)) {
            delete playerStatuses[teamType][playerName];
        }
    });
    
    // Initialize status for newly selected players
    selectedPlayerNames.forEach(playerName => {
        if (!playerStatuses[teamType][playerName]) {
            playerStatuses[teamType][playerName] = {
                status: 'questionable',
                probability: 0.5  // Default to 50% if questionable
            };
        }
    });
    
    // Reset styling
    countElement.style.color = '#666';
    countElement.style.fontWeight = 'normal';
    
    if (count === 0) {
        countElement.textContent = '0 players selected';
    } else {
        // Show which players are selected (for debugging)
        const playerNames = selectedPlayerNames.join(', ');
        countElement.textContent = `${count} player${count > 1 ? 's' : ''} selected`;
        countElement.title = `Selected: ${playerNames}`;
        countElement.style.color = '#dc3545';
        countElement.style.fontWeight = '600';
        
        console.log(`${teamType} team: ${count} injured player(s) - ${playerNames}`);
    }
    
    // Update status management UI
    updateStatusManagementUI();
}

function updateStatusManagementUI() {
    const managementDiv = document.getElementById('injury-status-management');
    const homePlayersDiv = document.getElementById('home-status-players');
    const visitorPlayersDiv = document.getElementById('visitor-status-players');
    
    if (!managementDiv || !homePlayersDiv || !visitorPlayersDiv) return;
    
    const homeSelected = Object.keys(playerStatuses.home);
    const visitorSelected = Object.keys(playerStatuses.visitor);
    const totalSelected = homeSelected.length + visitorSelected.length;
    
    // Show/hide management UI based on whether any players are selected
    if (totalSelected > 0) {
        managementDiv.classList.remove('hidden');
        
        // Render home team players
        renderStatusPlayers('home', homePlayersDiv, homeSelected, homeRoster);
        
        // Render visitor team players
        renderStatusPlayers('visitor', visitorPlayersDiv, visitorSelected, visitorRoster);
    } else {
        managementDiv.classList.add('hidden');
    }
}

function renderStatusPlayers(teamType, container, playerNames, roster) {
    container.innerHTML = '';
    
    if (playerNames.length === 0) {
        container.innerHTML = '<p style="color: #999; font-size: 0.85rem; font-style: italic;">No players selected</p>';
        return;
    }
    
    playerNames.forEach(playerName => {
        // Find player in roster to get type/position
        const player = roster.find(p => p.name === playerName);
        const playerType = player ? player.type : 'role';
        const playerPosition = player ? player.position : '';
        const typeIcon = playerType === 'star' ? '⭐' : playerType === 'key' ? '🔑' : '👥';
        
        const playerStatus = playerStatuses[teamType][playerName];
        
        const itemDiv = document.createElement('div');
        itemDiv.className = 'status-player-item';
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'status-player-name';
        nameDiv.textContent = `${typeIcon} ${playerName}${playerPosition ? ` (${playerPosition})` : ''}`;
        
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'status-player-controls';
        
        // Status selector
        const statusGroup = document.createElement('div');
        statusGroup.className = 'status-select-group';
        statusGroup.innerHTML = `
            <label>Status:</label>
            <select class="status-select" data-team="${teamType}" data-player="${playerName}" data-setting="status">
                <option value="out" ${playerStatus.status === 'out' ? 'selected' : ''}>Out (0%)</option>
                <option value="questionable" ${playerStatus.status === 'questionable' ? 'selected' : ''}>Questionable</option>
                <option value="available" ${playerStatus.status === 'available' ? 'selected' : ''}>Available (100%)</option>
            </select>
        `;
        
        // Probability slider (only shown for questionable)
        const probGroup = document.createElement('div');
        probGroup.className = 'probability-group';
        probGroup.style.display = playerStatus.status === 'questionable' ? 'flex' : 'none';
        probGroup.innerHTML = `
            <label>Probability:</label>
            <div class="probability-slider-container">
                <input type="range" min="1" max="99" value="${Math.round(playerStatus.probability * 100)}" 
                       class="probability-slider" data-team="${teamType}" data-player="${playerName}" data-setting="probability">
                <span class="probability-value">${Math.round(playerStatus.probability * 100)}%</span>
            </div>
        `;
        
        controlsDiv.appendChild(statusGroup);
        controlsDiv.appendChild(probGroup);
        
        itemDiv.appendChild(nameDiv);
        itemDiv.appendChild(controlsDiv);
        container.appendChild(itemDiv);
        
        // Add event listeners
        const statusSelect = statusGroup.querySelector('.status-select');
        statusSelect.addEventListener('change', function() {
            const status = this.value;
            playerStatuses[teamType][playerName].status = status;
            
            // Update probability based on status
            if (status === 'out') {
                playerStatuses[teamType][playerName].probability = 0.0;
            } else if (status === 'available') {
                playerStatuses[teamType][playerName].probability = 1.0;
            } else if (status === 'questionable') {
                // Keep current probability or default to 0.5
                if (!playerStatuses[teamType][playerName].probability || playerStatuses[teamType][playerName].probability === 0 || playerStatuses[teamType][playerName].probability === 1) {
                    playerStatuses[teamType][playerName].probability = 0.5;
                }
            }
            
            // Show/hide probability slider
            probGroup.style.display = status === 'questionable' ? 'flex' : 'none';
            if (status === 'questionable') {
                const slider = probGroup.querySelector('.probability-slider');
                const valueSpan = probGroup.querySelector('.probability-value');
                slider.value = Math.round(playerStatuses[teamType][playerName].probability * 100);
                valueSpan.textContent = `${Math.round(playerStatuses[teamType][playerName].probability * 100)}%`;
            }
        });
        
        const probSlider = probGroup.querySelector('.probability-slider');
        const probValue = probGroup.querySelector('.probability-value');
        if (probSlider) {
            probSlider.addEventListener('input', function() {
                const prob = parseInt(this.value) / 100.0;
                playerStatuses[teamType][playerName].probability = prob;
                probValue.textContent = `${this.value}%`;
            });
        }
    });
}

function getInjuryData() {
    // Get player statuses with probabilities
    const homePlayerStatuses = playerStatuses.home;
    const visitorPlayerStatuses = playerStatuses.visitor;
    
    // Convert to format: { playerName: probability } where probability is 0.0-1.0
    const homePlayers = {};
    const visitorPlayers = {};
    
    Object.keys(homePlayerStatuses).forEach(playerName => {
        const status = homePlayerStatuses[playerName];
        homePlayers[playerName] = status.probability;
    });
    
    Object.keys(visitorPlayerStatuses).forEach(playerName => {
        const status = visitorPlayerStatuses[playerName];
        visitorPlayers[playerName] = status.probability;
    });
    
    // Debug logging
    console.log('Injury data collected (with probabilities):', {
        home: homePlayers,
        visitor: visitorPlayers,
        homeCount: Object.keys(homePlayers).length,
        visitorCount: Object.keys(visitorPlayers).length
    });
    
    // Only return if there are players with status set
    if (Object.keys(homePlayers).length === 0 && Object.keys(visitorPlayers).length === 0) {
        console.log('No injuries selected, returning null');
        return null;
    }
    
    return {
        injured_players: {
            home: homePlayers,
            visitor: visitorPlayers
        }
    };
}

function clearInjuries() {
    clearTeamInjuries('home');
    clearTeamInjuries('visitor');
}

function clearTeamInjuries(teamType) {
    const selectElement = document.getElementById(`${teamType}-injured-players`);
    if (selectElement) {
        Array.from(selectElement.options).forEach(option => {
            if (!option.disabled) {
                option.selected = false;
            }
        });
    }
    
    // Clear player statuses
    playerStatuses[teamType] = {};
    
    updateSelectedCount(teamType);
    console.log(`Cleared injuries for ${teamType} team`);
}

function markNoInjuries(teamType) {
    // Clear any selected players and update the count
    clearTeamInjuries(teamType);
    
    // Visual feedback
    const countElement = document.getElementById(`${teamType}-selected-count`);
    if (countElement) {
        countElement.textContent = '✓ No injuries';
        countElement.style.color = '#28a745';
        countElement.style.fontWeight = '600';
        
        // Reset after 2 seconds
        setTimeout(() => {
            if (countElement.textContent === '✓ No injuries') {
                countElement.textContent = '0 players selected';
                countElement.style.color = '#666';
                countElement.style.fontWeight = 'normal';
            }
        }, 2000);
    }
}

async function makePrediction() {
    const homeTeamId = parseInt(document.getElementById('home-team').value);
    const visitorTeamId = parseInt(document.getElementById('visitor-team').value);
    const gameDate = document.getElementById('game-date').value;
    
    if (!homeTeamId || !visitorTeamId) {
        showError('Please select both teams');
        return;
    }
    
    if (homeTeamId === visitorTeamId) {
        showError('Please select different teams');
        return;
    }
    
    // Show loading, hide results and errors
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('prediction-result').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    
    try {
        const requestBody = {
            home_team_id: homeTeamId,
            visitor_team_id: visitorTeamId
        };
        
        if (gameDate) {
            requestBody.game_date = gameDate;
        }
        
        // Add injury data if manually set
        const injuryData = getInjuryData();
        if (injuryData) {
            requestBody.injury_data = injuryData;
            console.log('Including injury data in prediction request:', injuryData);
        } else {
            console.log('No injury data to include in prediction');
        }
        
        console.log('[PREDICT] Sending prediction request:', requestBody);
        
        // Add timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
        
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        console.log('[PREDICT] Response received:', response.status, response.statusText);
        
        if (!response.ok) {
            // Try to get error message from response
            let errorMessage = 'Prediction failed';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || `Server error (${response.status})`;
                if (errorData.traceback && config && config.FLASK_DEBUG) {
                    console.error('Server traceback:', errorData.traceback);
                }
            } catch (e) {
                errorMessage = `Server error: ${response.status} ${response.statusText}`;
            }
            showError(errorMessage);
            return;
        }
        
        const data = await response.json();
        console.log('[PREDICT] Response data:', data);
        
        if (data.success) {
            console.log('[PREDICT] Prediction successful, displaying results');
            displayPrediction(data.prediction, data.home_team, data.visitor_team);
        } else {
            console.error('[PREDICT] Prediction failed:', data.error);
            showError(data.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('[PREDICT] Prediction error:', error);
        if (error.name === 'AbortError') {
            showError('Prediction request timed out. The server may be processing slowly. Please try again.');
        } else {
            showError('Error making prediction: ' + error.message);
        }
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

function displayPrediction(prediction, homeTeam, visitorTeam) {
    console.log('[DISPLAY] Displaying prediction:', prediction);
    console.log('[DISPLAY] Home team:', homeTeam);
    console.log('[DISPLAY] Visitor team:', visitorTeam);
    
    // Check if required elements exist
    const homeTeamNameEl = document.getElementById('home-team-name');
    const visitorTeamNameEl = document.getElementById('visitor-team-name');
    
    if (!homeTeamNameEl || !visitorTeamNameEl) {
        console.error('[DISPLAY] Required elements not found!');
        showError('Error: Prediction result elements not found in page');
        return;
    }
    
    // Update team names
    homeTeamNameEl.textContent = homeTeam.full_name;
    visitorTeamNameEl.textContent = visitorTeam.full_name;
    
    // Update probabilities
    const homeProb = (prediction.home_win_probability * 100).toFixed(1);
    const visitorProb = (prediction.visitor_win_probability * 100).toFixed(1);
    
    document.getElementById('home-prob').textContent = homeProb + '%';
    document.getElementById('visitor-prob').textContent = visitorProb + '%';
    
    // Update money lines
    document.getElementById('home-ml').textContent = formatMoneyline(prediction.moneyline.home);
    document.getElementById('visitor-ml').textContent = formatMoneyline(prediction.moneyline.visitor);
    
    // Update predicted winner
    const predictedWinner = prediction.predicted_winner === 'home' ? 
        homeTeam.full_name : visitorTeam.full_name;
    document.getElementById('predicted-winner').textContent = predictedWinner;
    document.getElementById('favorite-team').textContent = 
        prediction.favorite_team === 'home' ? homeTeam.full_name : visitorTeam.full_name;
    
    // Update confidence
    const confidence = (prediction.confidence * 100).toFixed(0);
    document.getElementById('confidence-text').textContent = confidence + '%';
    
    // Highlight predicted winner
    const homeCard = document.querySelector('.home-team-card');
    const visitorCard = document.querySelector('.visitor-team-card');
    
    homeCard.classList.remove('predicted-winner');
    visitorCard.classList.remove('predicted-winner');
    
    if (prediction.predicted_winner === 'home') {
        homeCard.classList.add('predicted-winner');
    } else {
        visitorCard.classList.add('predicted-winner');
    }
    
    // Show result
    document.getElementById('prediction-result').classList.remove('hidden');
    
    // Scroll to result
    document.getElementById('prediction-result').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'nearest' 
    });
}

function formatMoneyline(ml) {
    if (ml === null || ml === undefined) return '-';
    return ml > 0 ? '+' + ml : ml.toString();
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

