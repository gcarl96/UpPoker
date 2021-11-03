import React, { Component } from 'react'
import io from 'socket.io-client'
import Seat from '../Seat/Seat'
import InputPanel from '../InputPanel/InputPanel'
import { Input } from '@material-ui/core'
import BlueCard from '../../resources/Cards/blue_back.png'
import WinningMessage from '../WinningMessage/WinningMessage'
import Grid from '@material-ui/core/Grid';
import backgroundImage from '../../resources/Table/Table.png'


const socket = io.connect()

class Game extends Component {
    constructor (props) {
        super(props)
        this.state = {
          username: '',
          gameData: null,
          playerData: null,
          room: this.props.match.params.roomId,
          cards: null,
          betAmount: 0
        }
        this.handleChange = this.handleChange.bind(this)
        this.joinRoom = this.joinRoom.bind(this)
        this.selectCard = this.selectCard.bind(this)
        this.deselectCard = this.deselectCard.bind(this)
        this.sendMessage = this.sendMessage.bind(this)
        this.setBetAmount = this.setBetAmount.bind(this)
      }
    
      handleChange (event) {
        const {name, value} = event.target
        this.setState({ [name]: value })
      }
    
      setSocketListeners () {
    
        socket.on('game_data', (data) => {
          this.setState({ gameData: data.msg || [] })
          var filtered = Object.fromEntries(Object.entries(this.state.gameData['players']).filter(([k,v]) => v['name'] === this.state.username))
          console.log(filtered)
          console.log("player: " + filtered[0])
          this.setState({ playerData: filtered[Object.keys(filtered)[0]]})
          this.setState({betAmount: this.state.gameData['currentBet'] - this.state.playerData['betAmount']})
          console.log(this.state.gameData);
        })

        socket.on('deal_cards', (data) => {
          this.setState({ cards: data.msg.map(function(card) {
            return {value : card,
                    selected: false}})
          })
        })
      }
    
      joinRoom (username, room) {
        this.setState({username: username})
        socket.emit('join_room', { username: username, room: room })
      }

      setBetAmount(amount) {
        this.setState({betAmount: amount})
      }

      selectCard(selectedCard) {
        if (!this.state.cards) {
          return;
        }
        if (this.state.cards.filter(x=> x['selected'] === true).length < 2) {
          var newCards = this.state.cards.map(card => {
            if (card['value'] === selectedCard['value']) {
              return {value : card['value'],
                      selected: true}
            } else {
              return {value : card['value'],
                      selected: card['selected']}
            }
          })
          this.setState({cards: newCards})
        }
      }

      deselectCard(selectedCard) {
        if (!this.state.cards) {
          return;
        }
        var newCards = this.state.cards.map(card => {
          if (card['value'] === selectedCard['value']) {
            return {value : card['value'],
                    selected: false}
          } else {
            return {value : card['value'],
                    selected: card['selected']}
          }
        })
        this.setState({cards: newCards})
      }
    
      sendMessage (action) {
        var modifier;
        switch(action) {
          case "Show":
            modifier = this.state.cards.filter(x=> x['selected'] === true).map(card => {
              return card['value'];
            });
            break;
          case "Bet":
            modifier = this.state.betAmount;
            break;
          default:
            modifier = 1;
            break;
        }
        console.log("Taking action: " + action + " with modifier: " + modifier)
        socket.emit(
          'take_action',
          {
            room: this.state.room,
            username: this.state.username,
            action,
            modifier
          }
        )
      }
    
      componentDidMount () {
        this.setSocketListeners()
        this.joinRoom(this.props.location.username,this.props.match.params.roomId)
      }

      getSeat(player, shifted_seat_number) {
        var cards = (player && player['name'] === this.state.username && this.state.cards) ? this.state.cards
        : ["DOWN", "DOWN", "DOWN", "DOWN"].map(function(card) { return {value : card,
                                        selected: false}})

        if (player['upCards'] && player['name'] != this.state.username) {
        cards = player['upCards']
        if (cards.length < 4) {
        cards = cards.concat(["DOWN", "DOWN"])
        }
        cards = cards.map(function(card) { return {value : card,
        selected: false}})
        }

        return player['name'] ? (
        <Seat playerData={player}
            seatNumber={shifted_seat_number}
            isCurrent={this.state.gameData['currentPlayer']===player['seat_number']}
            dealer={this.state.gameData['dealer']}
            smallBlind={this.state.gameData['smallBlind']}
            bigBlind={this.state.gameData['bigBlind']}
            cards={cards}
            selectCard={this.selectCard}
            deselectCard={this.deselectCard}/>
        ) : ( <div className={`seat-${shifted_seat_number}-container`}/> )
      }
    
      render () {
        const {username, gameData} = this.state

        const shiftedSeats = gameData ? Array(gameData['numSeats'])
                    .fill(null)
                    .map((_, i) => {            
                        console.log(i)            
                        const num_seats = this.state.gameData ? gameData['numSeats'] : 0
                        const seat_offset = this.state.playerData ? this.state.playerData['seat_number'] : 0

                        const shifted_seat_number = ((i + seat_offset) + num_seats) % num_seats
                        console.log(shifted_seat_number)
                        return shifted_seat_number
                    }) : [0]      
        console.log(shiftedSeats)
    
        if(gameData) {
            return (
                <div className='App'>
                  <div className="game-container">
                    <Grid container spacing={3} style={{backgroundImage: `url(${backgroundImage})`,   
                      height:'550px',
                      marginTop: 100, 
                      marginBottom: 70,
                      backgroundSize:'contain',
                      backgroundRepeat: 'no-repeat',
                      backgroundPosition: 'center'
                      }}>
                      <Grid item xs={12} align="center">
                        {
                          this.getSeat(gameData['players'][shiftedSeats[3]], 3)
                        }
                        {/* <div className={`seat-3-container`}/> */}
                      </Grid>
                      <Grid item xs={6} align="left">
                        {
                          this.getSeat(gameData['players'][shiftedSeats[2]], 2)
                        }
                      </Grid>
                      <Grid item xs={6} align="right">
                        {
                          this.getSeat(gameData['players'][shiftedSeats[4]], 4)
                        }
                      </Grid>
                      <Grid item xs={12} align="center" style={{height: 100}}>
                        <div className="board-container">
                          <p className="pot-value">{gameData['pot']}</p>
                          <div className="community-cards">
                            {gameData['communityCards']
                            .map(card => {
                              return <img className="card" src={require('../../resources/Cards/'+card+'.png').default} />
                            })}
                        </div>
                        <WinningMessage messages={this.state.gameData['winningMessages'] ? this.state.gameData['winningMessages'] : []}/>
                      </div>
                      </Grid>
                      <Grid item xs={6} align="left">
                        {
                          this.getSeat(gameData['players'][shiftedSeats[1]], 1)
                        }
                      </Grid>
                      <Grid item xs={6} align="right">
                        {
                          this.getSeat(gameData['players'][shiftedSeats[5]], 5)
                        }
                      </Grid>
                      <Grid item xs={12} align="center">
                       {
                          this.getSeat(gameData['players'][shiftedSeats[0]], 0)
                        }
                      </Grid>
                    </Grid>
                    {/* {Array(gameData['numSeats'])
                    .fill(null)
                    .map((_, i) => {
                        const player = gameData['players'][i]
                        
                        const num_seats = this.state.gameData ? gameData['numSeats'] : 0
                        const seat_offset = this.state.playerData ? this.state.playerData['seat_number'] : 0

                        const shifted_seat_number = (((i - seat_offset) % num_seats) + num_seats) % num_seats
                        var cards = (player && player['name'] === this.state.username && this.state.cards) ? this.state.cards
                                      : ["DOWN", "DOWN", "DOWN", "DOWN"].map(function(card) { return {value : card,
                                                                      selected: false}})

                        if (player['upCards'] && player['name'] != this.state.username) {
                          cards = player['upCards']
                          if (cards.length < 4) {
                            cards = cards.concat(["DOWN", "DOWN"])
                          }
                          cards = cards.map(function(card) { return {value : card,
                            selected: false}})
                        }

                        return player['name'] ? (
                            <Seat playerData={player}
                                  seatNumber={shifted_seat_number}
                                  isCurrent={gameData['currentPlayer']===player['seat_number']}
                                  dealer={gameData['dealer']}
                                  smallBlind={gameData['smallBlind']}
                                  bigBlind={gameData['bigBlind']}
                                  cards={cards}
                                  selectCard={this.selectCard}
                                  deselectCard={this.deselectCard}/>
                        ) : ( <div className={`seat-${shifted_seat_number}-container`}/> )
                    })} */}
                  </div>
                  <InputPanel state={this.state} makeAction={this.sendMessage} betAmount={this.state.betAmount} setBetAmount={this.setBetAmount}/>
                </div>
            )
        } else {
            return (
                <div className='App'>
                  <div className='header'>
                    <h1 className='title'>Up Poker</h1>
                  </div>
                </div>
            )
        }
        
      }
    }
    
export default Game
    