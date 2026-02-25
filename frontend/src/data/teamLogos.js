// Team logos mapping - using reliable public CDN sources
const TEAM_LOGOS = {
  // Serie A - Italy (using Sportmonks CDN)
  'Atalanta': 'https://cdn.sportmonks.com/images/soccer/teams/19/499.png',
  'Bologna': 'https://cdn.sportmonks.com/images/soccer/teams/20/500.png',
  'Cagliari': 'https://cdn.sportmonks.com/images/soccer/teams/10/490.png',
  'Como': 'https://cdn.sportmonks.com/images/soccer/teams/0/512.png',
  'Cremonese': 'https://cdn.sportmonks.com/images/soccer/teams/31/511.png',
  'Fiorentina': 'https://cdn.sportmonks.com/images/soccer/teams/22/502.png',
  'Genoa': 'https://cdn.sportmonks.com/images/soccer/teams/27/507.png',
  'Hellas Verona': 'https://cdn.sportmonks.com/images/soccer/teams/24/504.png',
  'Inter': 'https://cdn.sportmonks.com/images/soccer/teams/25/505.png',
  'Juventus': 'https://cdn.sportmonks.com/images/soccer/teams/16/496.png',
  'Lazio': 'https://cdn.sportmonks.com/images/soccer/teams/7/487.png',
  'Lecce': 'https://cdn.sportmonks.com/images/soccer/teams/3/867.png',
  'Milan': 'https://cdn.sportmonks.com/images/soccer/teams/9/489.png',
  'Napoli': 'https://cdn.sportmonks.com/images/soccer/teams/12/492.png',
  'Parma': 'https://cdn.sportmonks.com/images/soccer/teams/11/523.png',
  'Pisa': 'https://cdn.sportmonks.com/images/soccer/teams/2/514.png',
  'Roma': 'https://cdn.sportmonks.com/images/soccer/teams/17/497.png',
  'Sassuolo': 'https://cdn.sportmonks.com/images/soccer/teams/8/488.png',
  'Torino': 'https://cdn.sportmonks.com/images/soccer/teams/23/503.png',
  'Udinese': 'https://cdn.sportmonks.com/images/soccer/teams/14/494.png',
  'Empoli': 'https://cdn.sportmonks.com/images/soccer/teams/29/509.png',
  'Monza': 'https://cdn.sportmonks.com/images/soccer/teams/11/1579.png',
  'Venezia': 'https://cdn.sportmonks.com/images/soccer/teams/5/517.png',
  
  // Premier League - England
  'Arsenal': 'https://cdn.sportmonks.com/images/soccer/teams/10/42.png',
  'Aston Villa': 'https://cdn.sportmonks.com/images/soccer/teams/2/66.png',
  'Bournemouth': 'https://cdn.sportmonks.com/images/soccer/teams/3/35.png',
  'Brentford': 'https://cdn.sportmonks.com/images/soccer/teams/23/55.png',
  'Brighton': 'https://cdn.sportmonks.com/images/soccer/teams/19/51.png',
  'Burnley': 'https://cdn.sportmonks.com/images/soccer/teams/12/44.png',
  'Chelsea': 'https://cdn.sportmonks.com/images/soccer/teams/17/49.png',
  'Crystal Palace': 'https://cdn.sportmonks.com/images/soccer/teams/20/52.png',
  'Everton': 'https://cdn.sportmonks.com/images/soccer/teams/13/45.png',
  'Fulham': 'https://cdn.sportmonks.com/images/soccer/teams/4/36.png',
  'Leeds United': 'https://cdn.sportmonks.com/images/soccer/teams/31/63.png',
  'Liverpool': 'https://cdn.sportmonks.com/images/soccer/teams/8/40.png',
  'Manchester City': 'https://cdn.sportmonks.com/images/soccer/teams/18/50.png',
  'Manchester United': 'https://cdn.sportmonks.com/images/soccer/teams/1/33.png',
  'Newcastle United': 'https://cdn.sportmonks.com/images/soccer/teams/2/34.png',
  'Nottingham Forest': 'https://cdn.sportmonks.com/images/soccer/teams/1/65.png',
  'Sunderland': 'https://cdn.sportmonks.com/images/soccer/teams/7/71.png',
  'Tottenham': 'https://cdn.sportmonks.com/images/soccer/teams/15/47.png',
  'West Ham': 'https://cdn.sportmonks.com/images/soccer/teams/16/48.png',
  'Wolves': 'https://cdn.sportmonks.com/images/soccer/teams/7/39.png',
  
  // La Liga - Spain
  'Alavés': 'https://cdn.sportmonks.com/images/soccer/teams/30/542.png',
  'Athletic Bilbao': 'https://cdn.sportmonks.com/images/soccer/teams/19/531.png',
  'Atlético Madrid': 'https://cdn.sportmonks.com/images/soccer/teams/18/530.png',
  'Barcelona': 'https://cdn.sportmonks.com/images/soccer/teams/17/529.png',
  'Betis': 'https://cdn.sportmonks.com/images/soccer/teams/31/543.png',
  'Celta Vigo': 'https://cdn.sportmonks.com/images/soccer/teams/26/538.png',
  'Elche': 'https://cdn.sportmonks.com/images/soccer/teams/29/797.png',
  'Espanyol': 'https://cdn.sportmonks.com/images/soccer/teams/28/540.png',
  'Getafe': 'https://cdn.sportmonks.com/images/soccer/teams/2/546.png',
  'Girona': 'https://cdn.sportmonks.com/images/soccer/teams/3/547.png',
  'Levante': 'https://cdn.sportmonks.com/images/soccer/teams/27/539.png',
  'Mallorca': 'https://cdn.sportmonks.com/images/soccer/teams/30/798.png',
  'Osasuna': 'https://cdn.sportmonks.com/images/soccer/teams/23/727.png',
  'Oviedo': 'https://cdn.sportmonks.com/images/soccer/teams/20/724.png',
  'Rayo Vallecano': 'https://cdn.sportmonks.com/images/soccer/teams/24/728.png',
  'Real Madrid': 'https://cdn.sportmonks.com/images/soccer/teams/29/541.png',
  'Real Sociedad': 'https://cdn.sportmonks.com/images/soccer/teams/4/548.png',
  'Sevilla': 'https://cdn.sportmonks.com/images/soccer/teams/24/536.png',
  'Valencia': 'https://cdn.sportmonks.com/images/soccer/teams/20/532.png',
  'Villarreal': 'https://cdn.sportmonks.com/images/soccer/teams/21/533.png',
  
  // Bundesliga - Germany
  'Augsburg': 'https://cdn.sportmonks.com/images/soccer/teams/10/170.png',
  'Bayern Munich': 'https://cdn.sportmonks.com/images/soccer/teams/29/157.png',
  'Borussia Dortmund': 'https://cdn.sportmonks.com/images/soccer/teams/5/165.png',
  'Borussia Mönchengladbach': 'https://cdn.sportmonks.com/images/soccer/teams/3/163.png',
  'Eintracht Frankfurt': 'https://cdn.sportmonks.com/images/soccer/teams/9/169.png',
  'Freiburg': 'https://cdn.sportmonks.com/images/soccer/teams/0/160.png',
  'Hamburger SV': 'https://cdn.sportmonks.com/images/soccer/teams/20/180.png',
  'Heidenheim': 'https://cdn.sportmonks.com/images/soccer/teams/7/167.png',
  'Hoffenheim': 'https://cdn.sportmonks.com/images/soccer/teams/7/167.png',
  'Köln': 'https://cdn.sportmonks.com/images/soccer/teams/0/192.png',
  'Leverkusen': 'https://cdn.sportmonks.com/images/soccer/teams/8/168.png',
  'Mainz': 'https://cdn.sportmonks.com/images/soccer/teams/4/164.png',
  'RB Leipzig': 'https://cdn.sportmonks.com/images/soccer/teams/13/173.png',
  'St. Pauli': 'https://cdn.sportmonks.com/images/soccer/teams/26/186.png',
  'Stuttgart': 'https://cdn.sportmonks.com/images/soccer/teams/12/172.png',
  'Union Berlin': 'https://cdn.sportmonks.com/images/soccer/teams/22/182.png',
  'Werder Bremen': 'https://cdn.sportmonks.com/images/soccer/teams/2/162.png',
  'Wolfsburg': 'https://cdn.sportmonks.com/images/soccer/teams/1/161.png',
  
  // Liga Portugal
  'Arouca': 'https://cdn.sportmonks.com/images/soccer/teams/20/4716.png',
  'AVS': 'https://cdn.sportmonks.com/images/soccer/teams/10/810.png',
  'Benfica': 'https://cdn.sportmonks.com/images/soccer/teams/19/211.png',
  'Boavista': 'https://cdn.sportmonks.com/images/soccer/teams/30/222.png',
  'Braga': 'https://cdn.sportmonks.com/images/soccer/teams/25/217.png',
  'Casa Pia': 'https://cdn.sportmonks.com/images/soccer/teams/26/4282.png',
  'Estoril': 'https://cdn.sportmonks.com/images/soccer/teams/6/582.png',
  'Farense': 'https://cdn.sportmonks.com/images/soccer/teams/2/226.png',
  'Famalicão': 'https://cdn.sportmonks.com/images/soccer/teams/16/240.png',
  'Gil Vicente': 'https://cdn.sportmonks.com/images/soccer/teams/27/4283.png',
  'Moreirense': 'https://cdn.sportmonks.com/images/soccer/teams/31/223.png',
  'Nacional': 'https://cdn.sportmonks.com/images/soccer/teams/10/810.png',
  'Porto': 'https://cdn.sportmonks.com/images/soccer/teams/20/212.png',
  'Rio Ave': 'https://cdn.sportmonks.com/images/soccer/teams/23/215.png',
  'Santa Clara': 'https://cdn.sportmonks.com/images/soccer/teams/7/231.png',
  'Sporting CP': 'https://cdn.sportmonks.com/images/soccer/teams/4/228.png',
  'Estrela': 'https://cdn.sportmonks.com/images/soccer/teams/10/810.png',
  'Vitória Guimarães': 'https://cdn.sportmonks.com/images/soccer/teams/27/219.png',
  
  // Ligue 1 - France
  'PSG': 'https://cdn.sportmonks.com/images/soccer/teams/21/85.png',
  'Monaco': 'https://cdn.sportmonks.com/images/soccer/teams/27/91.png',
  'Marseille': 'https://cdn.sportmonks.com/images/soccer/teams/17/81.png',
  'Lyon': 'https://cdn.sportmonks.com/images/soccer/teams/16/80.png',
  'Angers': 'https://cdn.sportmonks.com/images/soccer/teams/13/77.png',
  'Le Havre': 'https://cdn.sportmonks.com/images/soccer/teams/30/94.png',
  
  // Super Lig - Turkey
  'Galatasaray': 'https://cdn.sportmonks.com/images/soccer/teams/21/645.png',
  'Fenerbahçe': 'https://cdn.sportmonks.com/images/soccer/teams/19/611.png',
  'Beşiktaş': 'https://cdn.sportmonks.com/images/soccer/teams/5/549.png',
  'Trabzonspor': 'https://cdn.sportmonks.com/images/soccer/teams/15/607.png',
  'Alanyaspor': 'https://cdn.sportmonks.com/images/soccer/teams/27/3563.png',
  'Antalyaspor': 'https://cdn.sportmonks.com/images/soccer/teams/21/3589.png',
  'Kocaelispor': 'https://cdn.sportmonks.com/images/soccer/teams/7/3575.png'
};

// League and Cup logos
const LEAGUE_LOGOS = {
  // Leagues
  'serie-a': 'https://cdn.sportmonks.com/images/soccer/leagues/7/135.png',
  'premier-league': 'https://cdn.sportmonks.com/images/soccer/leagues/7/39.png',
  'la-liga': 'https://cdn.sportmonks.com/images/soccer/leagues/12/140.png',
  'bundesliga': 'https://cdn.sportmonks.com/images/soccer/leagues/14/78.png',
  'ligue-1': 'https://cdn.sportmonks.com/images/soccer/leagues/29/61.png',
  'liga-portugal': 'https://cdn.sportmonks.com/images/soccer/leagues/30/94.png',
  'super-lig': 'https://cdn.sportmonks.com/images/soccer/leagues/11/203.png',
  
  // Cups
  'champions-league': 'https://cdn.sportmonks.com/images/soccer/leagues/2/2.png',
  'europa-league': 'https://cdn.sportmonks.com/images/soccer/leagues/3/3.png',
  'coppa-italia': 'https://cdn.sportmonks.com/images/soccer/leagues/9/137.png',
  'fa-cup': 'https://cdn.sportmonks.com/images/soccer/leagues/13/45.png',
  'copa-del-rey': 'https://cdn.sportmonks.com/images/soccer/leagues/15/143.png',
  'dfb-pokal': 'https://cdn.sportmonks.com/images/soccer/leagues/17/81.png',
  'coupe-de-france': 'https://cdn.sportmonks.com/images/soccer/leagues/2/66.png',
  'conference-league': 'https://cdn.sportmonks.com/images/soccer/leagues/16/848.png'
};

export const getTeamLogo = (teamName) => {
  return TEAM_LOGOS[teamName] || null;
};

export const getLeagueLogo = (leagueSlug) => {
  return LEAGUE_LOGOS[leagueSlug] || null;
};

export default TEAM_LOGOS;
