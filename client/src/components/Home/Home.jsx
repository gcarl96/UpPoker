import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Button, TextField } from '@material-ui/core';
import { Link } from "react-router-dom";
import "./Home.css"

class Home extends Component {

	constructor(props) {
		super(props)
		this.state = {
			username: '',
			room: ''
		}

		this.handleRoomJoin = this.handleRoomJoin.bind(this)
		this.handleChange = this.handleChange.bind(this)
	}

	handleRoomJoin(event) {
        event.preventDefault()
		const username = this.state.username
		const room = this.state.room
		if (username && room) {
			this.props.joinRoom(username, room)
		}
	}

	handleChange(event) {
		const { name, value } = event.target
		this.setState({ [name]: value })
	}

	renderUsernameTextField() {
		return (
			<div>
				<TextField
					required
					id="username"
					label="Player Name"
					variant="outlined"
					name="username"
					onChange={this.handleChange}
				/>
			</div>
		)
	}

	renderRoomTextField() {
		return (
			<div>
				<TextField
					required
					id="room"
					label="Room"
					variant="outlined"
					name="room"
					onChange={this.handleChange}
				/>
			</div>
		)
    }
    
    renderRoomButton(linkPath) {
        return(
            <Button
                component={Link}
                to={linkPath}
                variant='contained'
                color='primary'>
                Join Game
            </Button>
        )
    }

	render() {
		const linkPath = {
			pathname: "/" + this.state.room,
			username: this.state.username
		}

		return (
			<div className='App'>
				<div className='header'>
					<h1 className='title'>Up Poker</h1>
				</div>
				<div className='Home'>
					{this.renderUsernameTextField()}
					{this.renderRoomTextField()}
                    {this.renderRoomButton(linkPath)}
				</div>
			</div>
		)
	}
}

Home.propTypes = {
	joinRoom: PropTypes.func,
	setUsername: PropTypes.func,
}

export default Home
