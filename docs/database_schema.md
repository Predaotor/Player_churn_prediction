Table	Purpose	Granularity
players	Static info about each player	1 row per player
sessions	Login activity	1 row per session
bets	Each betting transaction	1 row per bet
deposits	Each deposit event	1 row per deposit
withdrawals	Each withdrawal event	1 row per withdrawal
bonuses	Promotions or bonuses given/redeemed	1 row per bonus event

We’ll then add a derived table player_features that aggregates all this data into features for the ML model.