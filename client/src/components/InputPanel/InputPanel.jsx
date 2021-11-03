import React, {useState} from 'react'
import {Grid, Button, Slider} from '@material-ui/core'

const calcAvailableActions = (gameData, playerData) => {
    var actions = [];
    if (!gameData || !playerData) {
        return actions;
    }
    if (gameData['readyToDeal']) {
        actions.push("Deal");
    }
    if (gameData['currentPlayer']!=playerData['seat_number']) {
        return actions
    }
    if (gameData['round'] === "Show") {
        actions.push("Show");
    } else {
        if (gameData['currentBet'] === playerData['betAmount']) {
            actions.push("Check");
        } else {
            actions.push("Call");
        }
        actions.push("Fold");
        actions.push("Bet");
        actions.push("Bet Amount")
    }
    return actions;
}

const ActionItem = (actionType, makeAction, minBetAmount, maxBetAmount, betAmount, setBetAmount) => {
    console.log(minBetAmount, maxBetAmount, betAmount);
    if (actionType === "Bet Amount") {
        if (maxBetAmount > 0) {
            return <Slider
                min={minBetAmount}
                max={maxBetAmount}
                value={betAmount}
                aria-labelledby="discrete-slider-always"
                onChange={ (e, val) => setBetAmount(val) }
                step={10}
                marks
                valueLabelDisplay="on"
            />
        } else {
            return <div></div>
        }
        
    } else {
        return <Button variant="contained" color="primary" onClick={() => { makeAction(actionType) }}>
                    {actionType}
                </Button>
    }
}
    

const InputPanel = ({state, makeAction, betAmount, setBetAmount}) => {
    const {username, gameData, playerData, room} = state
    const actions = calcAvailableActions(gameData, playerData);
    var minBetAmount = playerData ? gameData['currentBet'] - playerData['betAmount'] : 0
    var maxBetAmount = playerData ? playerData['chips'] : 0
    if (maxBetAmount < minBetAmount) {
        minBetAmount = maxBetAmount;
    }
    
    if (betAmount > maxBetAmount) {
        betAmount = maxBetAmount;
    }
    if (betAmount < minBetAmount) {
        betAmount = minBetAmount;
    }
    
    return (
        <div  className="App">
          <Grid container>
              {actions.map(action => (
                <Grid item xs={2}>
                    {ActionItem(action, makeAction, minBetAmount, maxBetAmount, betAmount, setBetAmount)}
                </Grid>
              ))
              }
          </Grid>
        </div>
      );
}

export default InputPanel