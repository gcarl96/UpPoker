import React from 'react'
import BlueCard from '../../resources/Cards/blue_back.png'

const getPositionString = (seat_number, dealer, smallBlind, bigBlind) => {
    var positionString = "";
    if(seat_number === dealer) {
        positionString += "D ";
    }
    if(seat_number === smallBlind) {
        positionString += "SB ";
    }
    if(seat_number === bigBlind) {
        positionString += "BB ";
    }

    return positionString;
}

const Seat = ({ playerData, seatNumber, isCurrent, dealer, smallBlind, bigBlind, cards, selectCard, deselectCard}) => {

    const {action, betAmount, chips, name, seat_number} = playerData
    const posString = getPositionString(seat_number, dealer, smallBlind, bigBlind);

    return (
        <div className={action === "Fold" ? `seat-${seatNumber}-container-fold` : isCurrent ? `seat-${seatNumber}-container-current`: `seat-${seatNumber}-container`}>
            <div className={`player-${seatNumber}-action-info-container`}>
                <h4 className="player-bet-amount">{betAmount}</h4>
                <h4 className="position-label">{posString}</h4>
            </div>
            {cards.map(card =>
                <img className={card['selected'] ? "card-selected" : "card"} src={card['value'] === "DOWN" ? BlueCard : require('../../resources/Cards/'+card['value']+'.png').default} onClick={() => {card['selected'] ? deselectCard(card) : selectCard(card)}} />
            )}
            <h4 className="player-name">{name}</h4>
            <h4 className="player-chip-count">{chips}</h4>
        </div>
    )
}

export default Seat