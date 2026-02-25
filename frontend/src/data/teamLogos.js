// Team logos mapping - using multiple reliable CDN sources
// - Transfermarkt (tmssl.akamaized.net) for Serie A
// - football-data.org for Premier League
// - Sportmonks as fallback

const TEAM_LOGOS = {
  // Serie A - Italy (using Transfermarkt CDN)
  'Atalanta': 'https://tmssl.akamaized.net/images/wappen/head/800.png',
  'Bologna': 'https://tmssl.akamaized.net/images/wappen/head/1025.png',
  'Cagliari': 'https://tmssl.akamaized.net/images/wappen/head/1390.png',
  'Como': 'https://tmssl.akamaized.net/images/wappen/head/1047.png',
  'Cremonese': 'https://tmssl.akamaized.net/images/wappen/head/2290.png',
  'Empoli': 'https://tmssl.akamaized.net/images/wappen/head/749.png',
  'Fiorentina': 'https://tmssl.akamaized.net/images/wappen/head/430.png',
  'Genoa': 'https://tmssl.akamaized.net/images/wappen/head/252.png',
  'Hellas Verona': 'https://tmssl.akamaized.net/images/wappen/head/276.png',
  'Inter': 'https://tmssl.akamaized.net/images/wappen/head/46.png',
  'Juventus': 'https://tmssl.akamaized.net/images/wappen/head/506.png',
  'Lazio': 'https://tmssl.akamaized.net/images/wappen/head/398.png',
  'Lecce': 'https://tmssl.akamaized.net/images/wappen/head/1005.png',
  'Milan': 'https://tmssl.akamaized.net/images/wappen/head/5.png',
  'Monza': 'https://tmssl.akamaized.net/images/wappen/head/2919.png',
  'Napoli': 'https://tmssl.akamaized.net/images/wappen/head/6195.png',
  'Parma': 'https://tmssl.akamaized.net/images/wappen/head/130.png',
  'Pisa': 'https://tmssl.akamaized.net/images/wappen/head/1057.png',
  'Roma': 'https://tmssl.akamaized.net/images/wappen/head/12.png',
  'Sassuolo': 'https://tmssl.akamaized.net/images/wappen/head/6574.png',
  'Torino': 'https://tmssl.akamaized.net/images/wappen/head/416.png',
  'Udinese': 'https://tmssl.akamaized.net/images/wappen/head/410.png',
  'Venezia': 'https://tmssl.akamaized.net/images/wappen/head/607.png',
  
  // Premier League - England (using Transfermarkt CDN)
  'Arsenal': 'https://tmssl.akamaized.net/images/wappen/head/11.png',
  'Aston Villa': 'https://tmssl.akamaized.net/images/wappen/head/405.png',
  'Bournemouth': 'https://tmssl.akamaized.net/images/wappen/head/989.png',
  'Brentford': 'https://tmssl.akamaized.net/images/wappen/head/1148.png',
  'Brighton': 'https://tmssl.akamaized.net/images/wappen/head/1237.png',
  'Burnley': 'https://tmssl.akamaized.net/images/wappen/head/1132.png',
  'Chelsea': 'https://tmssl.akamaized.net/images/wappen/head/631.png',
  'Crystal Palace': 'https://tmssl.akamaized.net/images/wappen/head/873.png',
  'Everton': 'https://tmssl.akamaized.net/images/wappen/head/29.png',
  'Fulham': 'https://tmssl.akamaized.net/images/wappen/head/931.png',
  'Leeds United': 'https://tmssl.akamaized.net/images/wappen/head/399.png',
  'Liverpool': 'https://tmssl.akamaized.net/images/wappen/head/31.png',
  'Manchester City': 'https://tmssl.akamaized.net/images/wappen/head/281.png',
  'Manchester United': 'https://tmssl.akamaized.net/images/wappen/head/985.png',
  'Newcastle United': 'https://tmssl.akamaized.net/images/wappen/head/762.png',
  'Nottingham Forest': 'https://tmssl.akamaized.net/images/wappen/head/703.png',
  'Sunderland': 'https://tmssl.akamaized.net/images/wappen/head/289.png',
  'Tottenham': 'https://tmssl.akamaized.net/images/wappen/head/148.png',
  'West Ham': 'https://tmssl.akamaized.net/images/wappen/head/379.png',
  'Wolves': 'https://tmssl.akamaized.net/images/wappen/head/543.png',
  
  // La Liga - Spain (using Transfermarkt CDN)
  'Alavés': 'https://tmssl.akamaized.net/images/wappen/head/1108.png',
  'Athletic Bilbao': 'https://tmssl.akamaized.net/images/wappen/head/621.png',
  'Atlético Madrid': 'https://tmssl.akamaized.net/images/wappen/head/13.png',
  'Barcelona': 'https://tmssl.akamaized.net/images/wappen/head/131.png',
  'Betis': 'https://tmssl.akamaized.net/images/wappen/head/150.png',
  'Celta Vigo': 'https://tmssl.akamaized.net/images/wappen/head/940.png',
  'Elche': 'https://tmssl.akamaized.net/images/wappen/head/1531.png',
  'Espanyol': 'https://tmssl.akamaized.net/images/wappen/head/714.png',
  'Getafe': 'https://tmssl.akamaized.net/images/wappen/head/3709.png',
  'Girona': 'https://tmssl.akamaized.net/images/wappen/head/12321.png',
  'Levante': 'https://tmssl.akamaized.net/images/wappen/head/3368.png',
  'Mallorca': 'https://tmssl.akamaized.net/images/wappen/head/237.png',
  'Osasuna': 'https://tmssl.akamaized.net/images/wappen/head/331.png',
  'Oviedo': 'https://tmssl.akamaized.net/images/wappen/head/2687.png',
  'Rayo Vallecano': 'https://tmssl.akamaized.net/images/wappen/head/367.png',
  'Real Madrid': 'https://tmssl.akamaized.net/images/wappen/head/418.png',
  'Real Sociedad': 'https://tmssl.akamaized.net/images/wappen/head/681.png',
  'Sevilla': 'https://tmssl.akamaized.net/images/wappen/head/368.png',
  'Valencia': 'https://tmssl.akamaized.net/images/wappen/head/1049.png',
  'Villarreal': 'https://tmssl.akamaized.net/images/wappen/head/1050.png',
  
  // Bundesliga - Germany (using Transfermarkt CDN)
  'Augsburg': 'https://tmssl.akamaized.net/images/wappen/head/167.png',
  'Bayern Munich': 'https://tmssl.akamaized.net/images/wappen/head/27.png',
  'Borussia Dortmund': 'https://tmssl.akamaized.net/images/wappen/head/16.png',
  'Borussia Mönchengladbach': 'https://tmssl.akamaized.net/images/wappen/head/18.png',
  'Eintracht Frankfurt': 'https://tmssl.akamaized.net/images/wappen/head/24.png',
  'Freiburg': 'https://tmssl.akamaized.net/images/wappen/head/60.png',
  'Hamburger SV': 'https://tmssl.akamaized.net/images/wappen/head/41.png',
  'Heidenheim': 'https://tmssl.akamaized.net/images/wappen/head/2036.png',
  'Hoffenheim': 'https://tmssl.akamaized.net/images/wappen/head/533.png',
  'Köln': 'https://tmssl.akamaized.net/images/wappen/head/3.png',
  'Leverkusen': 'https://tmssl.akamaized.net/images/wappen/head/15.png',
  'Mainz': 'https://tmssl.akamaized.net/images/wappen/head/39.png',
  'RB Leipzig': 'https://tmssl.akamaized.net/images/wappen/head/23826.png',
  'St. Pauli': 'https://tmssl.akamaized.net/images/wappen/head/35.png',
  'Stuttgart': 'https://tmssl.akamaized.net/images/wappen/head/79.png',
  'Union Berlin': 'https://tmssl.akamaized.net/images/wappen/head/89.png',
  'Werder Bremen': 'https://tmssl.akamaized.net/images/wappen/head/86.png',
  'Wolfsburg': 'https://tmssl.akamaized.net/images/wappen/head/82.png',
  
  // Liga Portugal (using Transfermarkt CDN)
  'Arouca': 'https://tmssl.akamaized.net/images/wappen/head/2778.png',
  'AVS': 'https://tmssl.akamaized.net/images/wappen/head/6718.png',
  'Benfica': 'https://tmssl.akamaized.net/images/wappen/head/294.png',
  'Boavista': 'https://tmssl.akamaized.net/images/wappen/head/1066.png',
  'Braga': 'https://tmssl.akamaized.net/images/wappen/head/1075.png',
  'Casa Pia': 'https://tmssl.akamaized.net/images/wappen/head/5530.png',
  'Estoril': 'https://tmssl.akamaized.net/images/wappen/head/2791.png',
  'Farense': 'https://tmssl.akamaized.net/images/wappen/head/2393.png',
  'Famalicão': 'https://tmssl.akamaized.net/images/wappen/head/3518.png',
  'Gil Vicente': 'https://tmssl.akamaized.net/images/wappen/head/4171.png',
  'Moreirense': 'https://tmssl.akamaized.net/images/wappen/head/3501.png',
  'Nacional': 'https://tmssl.akamaized.net/images/wappen/head/2791.png',
  'Porto': 'https://tmssl.akamaized.net/images/wappen/head/720.png',
  'Rio Ave': 'https://tmssl.akamaized.net/images/wappen/head/2796.png',
  'Santa Clara': 'https://tmssl.akamaized.net/images/wappen/head/14548.png',
  'Sporting CP': 'https://tmssl.akamaized.net/images/wappen/head/336.png',
  'Estrela': 'https://tmssl.akamaized.net/images/wappen/head/3369.png',
  'Vitória Guimarães': 'https://tmssl.akamaized.net/images/wappen/head/2420.png',
  
  // Ligue 1 - France (using Transfermarkt CDN)
  'PSG': 'https://tmssl.akamaized.net/images/wappen/head/583.png',
  'Monaco': 'https://tmssl.akamaized.net/images/wappen/head/162.png',
  'Marseille': 'https://tmssl.akamaized.net/images/wappen/head/244.png',
  'Lyon': 'https://tmssl.akamaized.net/images/wappen/head/1041.png',
  'Angers': 'https://tmssl.akamaized.net/images/wappen/head/1420.png',
  'Le Havre': 'https://tmssl.akamaized.net/images/wappen/head/738.png',
  
  // Super Lig - Turkey (using Transfermarkt CDN)
  'Galatasaray': 'https://tmssl.akamaized.net/images/wappen/head/141.png',
  'Fenerbahçe': 'https://tmssl.akamaized.net/images/wappen/head/36.png',
  'Beşiktaş': 'https://tmssl.akamaized.net/images/wappen/head/114.png',
  'Trabzonspor': 'https://tmssl.akamaized.net/images/wappen/head/449.png',
  'Alanyaspor': 'https://tmssl.akamaized.net/images/wappen/head/10484.png',
  'Antalyaspor': 'https://tmssl.akamaized.net/images/wappen/head/589.png',
  'Kocaelispor': 'https://tmssl.akamaized.net/images/wappen/head/3205.png'
};

// League and Cup logos (using Transfermarkt CDN)
const LEAGUE_LOGOS = {
  // Leagues
  'serie-a': 'https://tmssl.akamaized.net/images/logo/header/it1.png',
  'premier-league': 'https://tmssl.akamaized.net/images/logo/header/gb1.png',
  'la-liga': 'https://tmssl.akamaized.net/images/logo/header/es1.png',
  'bundesliga': 'https://tmssl.akamaized.net/images/logo/header/l1.png',
  'ligue-1': 'https://tmssl.akamaized.net/images/logo/header/fr1.png',
  'liga-portugal': 'https://tmssl.akamaized.net/images/logo/header/po1.png',
  'super-lig': 'https://tmssl.akamaized.net/images/logo/header/tr1.png',
  
  // Cups
  'champions-league': 'https://tmssl.akamaized.net/images/logo/header/cl.png',
  'europa-league': 'https://tmssl.akamaized.net/images/logo/header/el.png',
  'coppa-italia': 'https://tmssl.akamaized.net/images/logo/header/itpo.png',
  'fa-cup': 'https://tmssl.akamaized.net/images/logo/header/fac.png',
  'copa-del-rey': 'https://tmssl.akamaized.net/images/logo/header/cdr.png',
  'dfb-pokal': 'https://tmssl.akamaized.net/images/logo/header/dfb.png',
  'coupe-de-france': 'https://tmssl.akamaized.net/images/logo/header/cofr.png',
  'conference-league': 'https://tmssl.akamaized.net/images/logo/header/uecl.png'
};

// Helper function to normalize team names for lookup
const normalizeTeamName = (name) => {
  if (!name) return '';
  // Convert to title case for lookup
  return name.toLowerCase().split(' ').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

export const getTeamLogo = (teamName) => {
  if (!teamName) return null;
  // Try exact match first
  if (TEAM_LOGOS[teamName]) return TEAM_LOGOS[teamName];
  // Try normalized name (handles UPPERCASE from DB)
  const normalized = normalizeTeamName(teamName);
  if (TEAM_LOGOS[normalized]) return TEAM_LOGOS[normalized];
  // Try case-insensitive search
  const lowerName = teamName.toLowerCase();
  for (const [key, value] of Object.entries(TEAM_LOGOS)) {
    if (key.toLowerCase() === lowerName) return value;
  }
  return null;
};

export const getLeagueLogo = (leagueSlug) => {
  return LEAGUE_LOGOS[leagueSlug] || null;
};

export default TEAM_LOGOS;
