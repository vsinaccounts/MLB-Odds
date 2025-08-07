// Sports Betting Odds Frontend JavaScript

class OddsDisplay {
    constructor() {
        // Set to today's date in Eastern Time
        const now = new Date();
        const easternTime = new Date(now.toLocaleString('en-US', {timeZone: 'America/New_York'}));
        this.currentDate = new Date(easternTime.getFullYear(), easternTime.getMonth(), easternTime.getDate());
        
        this.currentSport = 'mlb';
        this.currentBetType = 'moneyline';
        this.oddsData = null;
        this.sportsbooks = [];
        
        // Define allowed sportsbooks based on actual uploaded logo files
        this.allowedSportsbooks = [
            'ESPN Bet',      // ESPN Bet.jpg
            'Fanatics',      // Fanatics.png
            'Caesars',       // Caesers.png (misspelled filename)
            'Bet365',        // Bet365.jpg
            'DraftKings',    // Draftkings.jpeg (lowercase k)
            'Unabated',      // Unabated.jpg
            'FanDuel',       // FanDuel.jpg
            'BetMGM'         // BetMGM.png
        ];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupScrollSync();
        this.updateDateDisplay();
        this.loadOddsData();
    }

    setupEventListeners() {
        // Sport selector
        document.getElementById('sport-selector').addEventListener('change', (e) => {
            this.currentSport = e.target.value;
            this.loadOddsData();
        });

        // Bet type selector
        document.getElementById('bet-type-selector').addEventListener('change', (e) => {
            this.currentBetType = e.target.value;
            this.renderTable();
        });

        // Date navigation
        document.getElementById('prev-date').addEventListener('click', () => {
            this.currentDate.setDate(this.currentDate.getDate() - 1);
            this.updateDateDisplay();
            this.loadOddsData();
        });

        document.getElementById('next-date').addEventListener('click', () => {
            this.currentDate.setDate(this.currentDate.getDate() + 1);
            this.updateDateDisplay();
            this.loadOddsData();
        });
    }

    setupScrollSync() {
        // Headers and games are now part of the same scrollable container
        // No sync needed as they scroll together naturally
    }

    updateDateDisplay() {
        const options = { 
            weekday: 'short', 
            month: 'short', 
            day: '2-digit',
            timeZone: 'America/New_York'
        };
        const dateStr = this.currentDate.toLocaleDateString('en-US', options);
        document.getElementById('current-date').textContent = `${dateStr} (ET)`;
    }

    async loadOddsData() {
        try {
            this.showLoading();
            
            // Try to load from API first, fallback to sample data
            let response;
            try {
                response = await fetch('http://localhost:5000/feed');
                if (!response.ok) throw new Error('API not available');
            } catch (apiError) {
                console.warn('API not available, loading sample data:', apiError);
                response = await fetch('./sample_output.json');
                if (!response.ok) {
                    response = await fetch('./test_output.json');
                }
            }
            
            this.oddsData = await response.json();
            this.extractSportsbooks();
            this.renderTable();
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading odds data:', error);
            this.showError();
        }
    }

    extractSportsbooks() {
        const sportsbooksSet = new Set();
        
        if (this.oddsData?.games) {
            this.oddsData.games.forEach(game => {
                if (game.odds) {
                    Object.values(game.odds).forEach(marketOdds => {
                        if (Array.isArray(marketOdds)) {
                            marketOdds.forEach(odd => {
                                if (odd.sportsbook) {
                                    sportsbooksSet.add(odd.sportsbook);
                                }
                            });
                        }
                    });
                }
            });
        }
        
        // Use supported sportsbooks from feed info if available
        if (this.oddsData?.feed_info?.supported_sportsbooks) {
            this.oddsData.feed_info.supported_sportsbooks.forEach(sb => {
                sportsbooksSet.add(sb);
            });
        }
        
        // Filter to only include allowed sportsbooks
        const allSportsbooks = Array.from(sportsbooksSet);
        this.sportsbooks = this.filterAllowedSportsbooks(allSportsbooks);
        this.renderSportsbookHeaders();
    }

    // Helper method to normalize sportsbook names for comparison
    normalizeSportsbookName(name) {
        return name.toLowerCase()
            .replace(/\s+/g, '')
            .replace(/[^a-z0-9]/g, '');
    }

    // Filter sportsbooks to only include allowed ones
    filterAllowedSportsbooks(allSportsbooks) {
        const filtered = [];
        
        // Create normalized versions of allowed sportsbooks for comparison
        const normalizedAllowed = this.allowedSportsbooks.map(sb => ({
            original: sb,
            normalized: this.normalizeSportsbookName(sb)
        }));
        
        allSportsbooks.forEach(sportsbook => {
            const normalizedSportsbook = this.normalizeSportsbookName(sportsbook);
            
            // Check if this sportsbook matches any of our allowed ones
            const match = normalizedAllowed.find(allowed => 
                allowed.normalized === normalizedSportsbook ||
                normalizedSportsbook.includes(allowed.normalized) ||
                allowed.normalized.includes(normalizedSportsbook)
            );
            
            if (match) {
                filtered.push(sportsbook);
            }
        });
        
        // If no matches found from data, return the allowed sportsbooks 
        // (they may not have data but we still want to show headers)
        if (filtered.length === 0) {
            return this.allowedSportsbooks.slice(); // Return copy of allowed sportsbooks
        }
        
        return filtered;
    }

    // Check if a sportsbook is in our allowed list
    isAllowedSportsbook(sportsbook) {
        const normalizedSportsbook = this.normalizeSportsbookName(sportsbook);
        
        return this.allowedSportsbooks.some(allowed => {
            const normalizedAllowed = this.normalizeSportsbookName(allowed);
            return normalizedAllowed === normalizedSportsbook ||
                   normalizedSportsbook.includes(normalizedAllowed) ||
                   normalizedAllowed.includes(normalizedSportsbook);
        });
    }

    getSportsbookLogoUrl(sportsbook) {
        // First try local uploaded logos - these take priority
        const localLogoUrl = this.getLocalLogoUrl(sportsbook);
        if (localLogoUrl) {
            return localLogoUrl;
        }

        // Fallback to external URLs if local logos aren't available
        const logoMap = {
            // Allowed sportsbooks - external fallbacks
            'ESPN Bet': 'https://cdn.jsdelivr.net/gh/simple-icons/simple-icons@v9/icons/espn.svg',
            'Fanatics': 'https://seeklogo.com/images/F/fanatics-logo-2B2A928BDC-seeklogo.com.png',
            'Caesars': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Caesars_Palace_logo.svg/200px-Caesars_Palace_logo.svg.png',
            'Bet365': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Bet365_logo.svg/200px-Bet365_logo.svg.png',
            'DraftKings': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/DraftKings_logo.svg/200px-DraftKings_logo.svg.png',
            'Unabated': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHJ4PSI2IiBmaWxsPSIjNGE5MGUyIi8+CiAgPHRleHQgeD0iMTYiIHk9IjIyIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTYiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+VTwvdGV4dD4KICA8L3N2Zz4=',
            'FanDuel': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/FanDuel_logo.svg/200px-FanDuel_logo.svg.png',
            'BetMGM': 'https://seeklogo.com/images/B/betmgm-logo-160AE4D76B-seeklogo.com.png',
            
            // Other sportsbooks (for backward compatibility)
            'BetRivers': 'https://www.gamblingsites.com/app/uploads/2019/10/betrivers-logo-1.png',
            'PointsBet': 'https://logos-world.net/wp-content/uploads/2021/08/PointsBet-Logo.png',
            'WynnBET': 'https://logos-world.net/wp-content/uploads/2021/08/WynnBET-Logo.png',
            'Bovada': 'https://www.gamblingsites.com/app/uploads/2019/10/bovada-logo-1.png',
            'BetOnline': 'https://www.gamblingsites.com/app/uploads/2019/10/betonline-logo-1.png',
            'Bookmaker': 'https://www.gamblingsites.com/app/uploads/2019/10/bookmaker-logo-1.png',
            'Pinnacle': 'https://www.gamblingsites.com/app/uploads/2019/10/pinnacle-logo-1.png',
            'Circa': 'https://www.gamblingsites.com/app/uploads/2020/10/circa-sports-logo.png',
            'Barstool': 'https://logos-world.net/wp-content/uploads/2021/08/Barstool-Sportsbook-Logo.png',
            'BetUS': 'https://www.gamblingsites.com/app/uploads/2019/10/betus-logo-1.png',
            'MyBookie': 'https://www.gamblingsites.com/app/uploads/2019/10/mybookie-logo-1.png',
            'SportsBetting': 'https://www.gamblingsites.com/app/uploads/2019/10/sportsbetting-logo-1.png',
            'Unibet': 'https://logos-world.net/wp-content/uploads/2020/06/Unibet-Logo.png',
            'BetFred': 'https://logos-world.net/wp-content/uploads/2021/08/Betfred-Logo.png',
            'TwinSpires': 'https://www.gamblingsites.com/app/uploads/2020/05/twinspires-logo.png'
        };

        // Try exact match first
        if (logoMap[sportsbook]) {
            return logoMap[sportsbook];
        }

        // Try case-insensitive match
        const lowerSportsbook = sportsbook.toLowerCase();
        for (const [key, url] of Object.entries(logoMap)) {
            if (key.toLowerCase() === lowerSportsbook) {
                return url;
            }
        }

        // Return null for fallback handling
        return null;
    }

    getLocalLogoUrl(sportsbook) {
        // Map of sportsbook names to their exact uploaded file names
        const fileMap = {
            'ESPN Bet': 'ESPN Bet.jpg',        // Note: space in filename
            'Fanatics': 'Fanatics.png', 
            'Caesars': 'Caesers.png',          // Note: misspelled as "Caesers" in actual file
            'Bet365': 'Bet365.jpg',
            'DraftKings': 'Draftkings.jpeg',   // Note: lowercase 'k' in actual file
            'Unabated': 'Unabated.jpg',
            'FanDuel': 'FanDuel.jpg',
            'BetMGM': 'BetMGM.png'
        };
        
        // Check if we have a specific file mapping for this sportsbook
        if (fileMap[sportsbook]) {
            return `http://localhost:5000/logos/${fileMap[sportsbook]}`;
        }
        
        // Return null if no mapping found (will trigger fallback)
        return null;
    }

    createFallbackLogo(sportsbook) {
        // Create a styled SVG fallback logo
        const initial = sportsbook.charAt(0).toUpperCase();
        const colors = {
            // Allowed sportsbooks colors
            'ESPN Bet': '#d50000',
            'Fanatics': '#0066cc', 
            'Caesars': '#dc2626',
            'Bet365': '#ffb400',
            'DraftKings': '#f59e0b',
            'Unabated': '#4a90e2',
            'FanDuel': '#1e3a8a',
            'BetMGM': '#059669',
            
            // Other sportsbooks
            'BetRivers': '#0891b2',
            'PointsBet': '#7c3aed',
            'WynnBET': '#be123c',
            'Bovada': '#ea580c',
            'BetOnline': '#16a34a',
            'Bookmaker': '#0f172a',
            'Pinnacle': '#dc2626',
            'Circa': '#f59e0b'
        };
        
        const color = colors[sportsbook] || '#4a90e2';
        
        return `data:image/svg+xml;base64,${btoa(`
            <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="6" fill="${color}"/>
                <text x="16" y="22" font-family="Arial, sans-serif" font-size="16" font-weight="bold" 
                      fill="white" text-anchor="middle">${initial}</text>
            </svg>
        `)}`;
    }

    renderSportsbookHeaders() {
        const container = document.getElementById('sportsbook-headers');
        container.innerHTML = '';

        this.sportsbooks.forEach(sportsbook => {
            const header = document.createElement('div');
            header.className = 'sportsbook-header';
            
            const externalLogoUrl = this.getSportsbookLogoUrl(sportsbook);
            const localLogoUrl = this.getLocalLogoUrl(sportsbook);
            const fallbackLogo = this.createFallbackLogo(sportsbook);
            
            const img = document.createElement('img');
            img.alt = sportsbook;
            img.className = 'sportsbook-logo loading';
            
            // Multi-tier fallback system - prioritize local files
            let currentTier = 0;
            const tryNextLogo = () => {
                img.classList.remove('loading', 'fallback');
                
                if (currentTier === 0 && localLogoUrl) {
                    // Tier 1: Try local server logo first
                    console.log(`Loading local logo for ${sportsbook}: ${localLogoUrl}`);
                    img.className = 'sportsbook-logo loading';
                    img.src = localLogoUrl;
                    currentTier++;
                } else if (currentTier === 1 && externalLogoUrl) {
                    // Tier 2: Try external logo URL
                    console.log(`Loading external logo for ${sportsbook}: ${externalLogoUrl}`);
                    img.className = 'sportsbook-logo loading';
                    img.src = externalLogoUrl;
                    currentTier++;
                } else {
                    // Tier 3: Use generated fallback
                    console.log(`Using fallback logo for ${sportsbook}`);
                    img.classList.remove('loading');
                    img.classList.add('fallback');
                    img.src = fallbackLogo;
                }
            };
            
            img.onload = () => {
                img.classList.remove('loading');
            };
            
            img.onerror = () => {
                console.log(`Logo failed to load for ${sportsbook} at tier ${currentTier}, src: ${img.src}`);
                if (currentTier === 0 && !localLogoUrl && externalLogoUrl) {
                    // Skip to external if no local logo exists
                    currentTier = 1;
                    tryNextLogo();
                } else if (currentTier < 2) {
                    currentTier++;
                    tryNextLogo();
                } else {
                    console.log(`Using final fallback for ${sportsbook}`);
                    img.classList.remove('loading');
                    img.classList.add('fallback');
                    img.src = fallbackLogo;
                }
            };
            
            // Start with first tier
            tryNextLogo();
            
            const nameDiv = document.createElement('div');
            nameDiv.className = 'sportsbook-name';
            nameDiv.textContent = this.formatSportsbookName(sportsbook);
            
            header.appendChild(img);
            header.appendChild(nameDiv);
            container.appendChild(header);
        });
    }

    formatSportsbookName(name) {
        // Handle common sportsbook name formatting
        const nameMap = {
            // Allowed sportsbooks
            'ESPN Bet': 'ESPN BET',
            'Fanatics': 'FANATICS',
            'Caesars': 'CAESARS',
            'Bet365': 'BET365',
            'DraftKings': 'DRAFTKINGS',
            'Unabated': 'UNABATED',
            'FanDuel': 'FANDUEL',
            'BetMGM': 'BETMGM',
            
            // Other sportsbooks
            'BetRivers': 'BETRIVERS',
            'PointsBet': 'POINTSBET',
            'WynnBET': 'WYNNBET'
        };
        
        return nameMap[name] || name.toUpperCase();
    }

    renderTable() {
        if (!this.oddsData?.games) {
            this.showError();
            return;
        }

        const container = document.getElementById('games-table');
        container.innerHTML = '';

        // Filter, deduplicate, and sort games
        const filteredGames = this.filterGamesByDate(this.oddsData.games);
        console.log(`Filtered to ${filteredGames.length} games for selected date`);
        
        const uniqueGames = this.removeDuplicateGames(filteredGames);
        console.log(`After removing duplicates: ${uniqueGames.length} games`);
        
        const sortedGames = this.sortGamesByTime(uniqueGames);

        if (sortedGames.length === 0) {
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #636e72;">
                    No games scheduled for this date.
                </div>
            `;
            return;
        }

        sortedGames.forEach(game => {
            const gameRow = this.createGameRow(game);
            container.appendChild(gameRow);
        });
    }

    filterGamesByDate(games) {
        const selectedDate = new Date(this.currentDate);
        
        return games.filter(game => {
            // Parse game time as UTC and convert to Eastern Time
            const gameTime = new Date(game.game_time + 'Z');
            const gameET = new Date(gameTime.toLocaleString('en-US', {timeZone: 'America/New_York'}));
            
            // Check if game is on the selected date in Eastern Time
            const selectedYear = selectedDate.getFullYear();
            const selectedMonth = selectedDate.getMonth();
            const selectedDay = selectedDate.getDate();
            
            const gameYear = gameET.getFullYear();
            const gameMonth = gameET.getMonth();
            const gameDay = gameET.getDate();
            
            return gameYear === selectedYear && gameMonth === selectedMonth && gameDay === selectedDay;
        });
    }

    removeDuplicateGames(games) {
        const seen = new Map();
        const uniqueGames = [];
        
        games.forEach(game => {
            // Create a unique key based on teams and approximate game time (within same hour)
            const gameDate = new Date(game.game_time);
            const hourKey = `${gameDate.getFullYear()}-${gameDate.getMonth()}-${gameDate.getDate()}-${gameDate.getHours()}`;
            const teamsKey = `${game.away_team}_vs_${game.home_team}_${hourKey}`;
            
            if (!seen.has(teamsKey)) {
                seen.set(teamsKey, true);
                uniqueGames.push(game);
            } else {
                // If we've seen this matchup, merge the odds data to get more complete information
                const existingGameIndex = uniqueGames.findIndex(g => {
                    const existingDate = new Date(g.game_time);
                    const existingHourKey = `${existingDate.getFullYear()}-${existingDate.getMonth()}-${existingDate.getDate()}-${existingDate.getHours()}`;
                    const existingTeamsKey = `${g.away_team}_vs_${g.home_team}_${existingHourKey}`;
                    return existingTeamsKey === teamsKey;
                });
                
                if (existingGameIndex !== -1) {
                    // Merge odds data from duplicate game
                    const existingGame = uniqueGames[existingGameIndex];
                    this.mergeGameOdds(existingGame, game);
                }
            }
        });
        
        return uniqueGames;
    }

    mergeGameOdds(existingGame, newGame) {
        // Merge odds from newGame into existingGame
        if (newGame.odds) {
            Object.keys(newGame.odds).forEach(marketType => {
                if (!existingGame.odds) {
                    existingGame.odds = {};
                }
                if (!existingGame.odds[marketType]) {
                    existingGame.odds[marketType] = [];
                }
                
                // Add new sportsbook odds that don't already exist
                newGame.odds[marketType].forEach(newOdds => {
                    const existingOddsIndex = existingGame.odds[marketType].findIndex(
                        existing => existing.sportsbook === newOdds.sportsbook
                    );
                    
                    if (existingOddsIndex === -1) {
                        existingGame.odds[marketType].push(newOdds);
                    } else {
                        // Update if the new odds are more recent
                        const existingTime = new Date(existingGame.odds[marketType][existingOddsIndex].last_updated);
                        const newTime = new Date(newOdds.last_updated);
                        if (newTime > existingTime) {
                            existingGame.odds[marketType][existingOddsIndex] = newOdds;
                        }
                    }
                });
            });
        }
    }

    sortGamesByTime(games) {
        return games.sort((a, b) => {
            const timeA = new Date(a.game_time);
            const timeB = new Date(b.game_time);
            return timeA - timeB;
        });
    }

    createGameRow(game) {
        const row = document.createElement('div');
        row.className = 'game-row';

        // Parse the UTC time and convert to Eastern Time
        const gameTime = new Date(game.game_time + 'Z'); // Ensure UTC parsing
        const timeStr = gameTime.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true,
            timeZone: 'America/New_York'
        });

        // Get odds for current bet type
        const marketOdds = game.odds?.[this.currentBetType] || [];
        const bestOdds = this.findBestOdds(marketOdds);

        row.innerHTML = `
            <div class="game-info">
                <div class="game-time">
                    <div class="time">${timeStr}</div>
                </div>
                <div class="teams">
                    <div class="team away-team">
                        <img src="https://via.placeholder.com/20x20/e74c3c/ffffff?text=${game.away_team.charAt(0)}" 
                             alt="${game.away_team}" 
                             class="team-logo"
                             onerror="this.style.display='none'">
                        <span class="team-name">${this.formatTeamName(game.away_team)}</span>
                    </div>
                    <div class="team home-team">
                        <img src="https://via.placeholder.com/20x20/2d3436/ffffff?text=${game.home_team.charAt(0)}" 
                             alt="${game.home_team}" 
                             class="team-logo"
                             onerror="this.style.display='none'">
                        <span class="team-name">${this.formatTeamName(game.home_team)}</span>
                    </div>
                </div>
                <div class="best-odds-section">
                    ${this.renderBestOdds(bestOdds)}
                </div>
            </div>
            <div class="sportsbook-odds">
                ${this.renderSportsbookOdds(marketOdds, bestOdds)}
            </div>
        `;

        return row;
    }

    formatTeamName(teamName) {
        // Extract team name from full name (e.g., "New York Yankees" -> "Yankees")
        const parts = teamName.split(' ');
        return parts[parts.length - 1];
    }

    findBestOdds(marketOdds) {
        if (!Array.isArray(marketOdds) || marketOdds.length === 0) {
            return null;
        }

        let bestAway = null;
        let bestHome = null;

        // Filter market odds to only include allowed sportsbooks
        const filteredMarketOdds = marketOdds.filter(odds => 
            this.isAllowedSportsbook(odds.sportsbook)
        );

        filteredMarketOdds.forEach(odds => {
            if (this.currentBetType === 'moneyline') {
                if (odds.away_team?.odds) {
                    if (!bestAway || this.isBetterOdds(odds.away_team.odds, bestAway.odds, odds.away_team.odds > 0)) {
                        bestAway = { odds: odds.away_team.odds, sportsbook: odds.sportsbook };
                    }
                }
                if (odds.home_team?.odds) {
                    if (!bestHome || this.isBetterOdds(odds.home_team.odds, bestHome.odds, odds.home_team.odds > 0)) {
                        bestHome = { odds: odds.home_team.odds, sportsbook: odds.sportsbook };
                    }
                }
            } else if (this.currentBetType === 'spread') {
                if (odds.away_team?.odds) {
                    if (!bestAway || this.isBetterOdds(odds.away_team.odds, bestAway.odds, false)) {
                        bestAway = { 
                            odds: odds.away_team.odds, 
                            spread: odds.away_team.spread,
                            sportsbook: odds.sportsbook 
                        };
                    }
                }
                if (odds.home_team?.odds) {
                    if (!bestHome || this.isBetterOdds(odds.home_team.odds, bestHome.odds, false)) {
                        bestHome = { 
                            odds: odds.home_team.odds, 
                            spread: odds.home_team.spread,
                            sportsbook: odds.sportsbook 
                        };
                    }
                }
            } else if (this.currentBetType === 'total') {
                if (odds.over?.odds) {
                    if (!bestAway || this.isBetterOdds(odds.over.odds, bestAway.odds, false)) {
                        bestAway = { 
                            odds: odds.over.odds, 
                            total: odds.total,
                            type: 'over',
                            sportsbook: odds.sportsbook 
                        };
                    }
                }
                if (odds.under?.odds) {
                    if (!bestHome || this.isBetterOdds(odds.under.odds, bestHome.odds, false)) {
                        bestHome = { 
                            odds: odds.under.odds, 
                            total: odds.total,
                            type: 'under',
                            sportsbook: odds.sportsbook 
                        };
                    }
                }
            }
        });

        return { away: bestAway, home: bestHome };
    }

    isBetterOdds(newOdds, currentOdds, isPositive) {
        if (isPositive) {
            // For positive odds, higher is better
            return newOdds > currentOdds;
        } else {
            // For negative odds, closer to 0 is better (less negative)
            return Math.abs(newOdds) < Math.abs(currentOdds);
        }
    }

    renderBestOdds(bestOdds) {
        if (!bestOdds) {
            return '<div class="best-odds-row">No odds available</div>';
        }

        let awayDisplay = 'N/A';
        let homeDisplay = 'N/A';

        if (bestOdds.away) {
            if (this.currentBetType === 'spread') {
                awayDisplay = `${this.formatSpread(bestOdds.away.spread)} ${this.formatOdds(bestOdds.away.odds)}`;
            } else if (this.currentBetType === 'total') {
                awayDisplay = `O${bestOdds.away.total} ${this.formatOdds(bestOdds.away.odds)}`;
            } else {
                awayDisplay = this.formatOdds(bestOdds.away.odds);
            }
        }

        if (bestOdds.home) {
            if (this.currentBetType === 'spread') {
                homeDisplay = `${this.formatSpread(bestOdds.home.spread)} ${this.formatOdds(bestOdds.home.odds)}`;
            } else if (this.currentBetType === 'total') {
                homeDisplay = `U${bestOdds.home.total} ${this.formatOdds(bestOdds.home.odds)}`;
            } else {
                homeDisplay = this.formatOdds(bestOdds.home.odds);
            }
        }

        return `
            <div class="best-odds-row">
                <span class="best-odds-value ${this.getOddsClass(bestOdds.away?.odds)} best">
                    ${awayDisplay}
                    <span class="best-indicator">★</span>
                </span>
            </div>
            <div class="best-odds-row">
                <span class="best-odds-value ${this.getOddsClass(bestOdds.home?.odds)} best">
                    ${homeDisplay}
                    <span class="best-indicator">★</span>
                </span>
            </div>
        `;
    }

    renderSportsbookOdds(marketOdds, bestOdds) {
        return this.sportsbooks.map(sportsbook => {
            // Only show odds for sportsbooks that are in our filtered list
            const odds = marketOdds.find(o => o.sportsbook === sportsbook);
            return this.renderOddsColumn(odds, bestOdds, sportsbook);
        }).join('');
    }

    renderOddsColumn(odds, bestOdds, sportsbook) {
        if (!odds) {
            return `
                <div class="odds-column">
                    <div class="odds-value unavailable">N/A</div>
                    <div class="odds-value unavailable">N/A</div>
                </div>
            `;
        }

        let awayOdds = null;
        let homeOdds = null;
        let awayDisplay = 'N/A';
        let homeDisplay = 'N/A';

        if (this.currentBetType === 'moneyline') {
            awayOdds = odds.away_team?.odds;
            homeOdds = odds.home_team?.odds;
            awayDisplay = awayOdds ? this.formatOdds(awayOdds) : 'N/A';
            homeDisplay = homeOdds ? this.formatOdds(homeOdds) : 'N/A';
        } else if (this.currentBetType === 'spread') {
            awayOdds = odds.away_team?.odds;
            homeOdds = odds.home_team?.odds;
            awayDisplay = awayOdds ? `${this.formatSpread(odds.away_team.spread)} ${this.formatOdds(awayOdds)}` : 'N/A';
            homeDisplay = homeOdds ? `${this.formatSpread(odds.home_team.spread)} ${this.formatOdds(homeOdds)}` : 'N/A';
        } else if (this.currentBetType === 'total') {
            awayOdds = odds.over?.odds;
            homeOdds = odds.under?.odds;
            awayDisplay = awayOdds ? `O${odds.total} ${this.formatOdds(awayOdds)}` : 'N/A';
            homeDisplay = homeOdds ? `U${odds.total} ${this.formatOdds(homeOdds)}` : 'N/A';
        }

        const awayIsBest = bestOdds?.away?.sportsbook === sportsbook;
        const homeIsBest = bestOdds?.home?.sportsbook === sportsbook;

        return `
            <div class="odds-column">
                <div class="odds-value ${this.getOddsClass(awayOdds)} ${awayIsBest ? 'best' : ''}">
                    ${awayDisplay}
                </div>
                <div class="odds-value ${this.getOddsClass(homeOdds)} ${homeIsBest ? 'best' : ''}">
                    ${homeDisplay}
                </div>
            </div>
        `;
    }

    formatOdds(odds) {
        if (odds === null || odds === undefined) return 'N/A';
        return odds > 0 ? `+${odds}` : `${odds}`;
    }

    formatSpread(spread) {
        if (spread === null || spread === undefined) return '';
        return spread > 0 ? `+${spread}` : `${spread}`;
    }

    getOddsClass(odds) {
        if (odds === null || odds === undefined) return 'unavailable';
        return odds > 0 ? 'positive' : 'negative';
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('error').classList.add('hidden');
        document.querySelector('.table-container').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
        document.querySelector('.table-container').style.display = 'block';
    }

    showError() {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('error').classList.remove('hidden');
        document.querySelector('.table-container').style.display = 'none';
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.oddsDisplay = new OddsDisplay();
});

// Global function for retry button
function loadOddsData() {
    if (window.oddsDisplay) {
        window.oddsDisplay.loadOddsData();
    }
}