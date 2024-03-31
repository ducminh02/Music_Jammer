import React, { Component } from "react";
import {Grid, Button, Typography} from "@material-ui/core";
import CreateRoomPage from "./CreateRoomPage";


export default class Room extends Component {
    constructor(props) {
        super(props);
        this.state = {
            votesToSkip: 2,
            guestCanPause: false,
            isHost: false,
            showsSetting: false,
            spotifyAuthenticated: false,
            song: {},
        };
        this.roomCode = this.props.match.params.roomCode;
        this._leaveThisButtonPress = this._leaveThisButtonPress.bind(this);
        this._updateShowsSetting = this._updateShowsSetting.bind(this);
        this._renderSettingsButton = this._renderSettingsButton.bind(this);
        this._renderSettings = this._renderSettings.bind(this);
        this._getRoomDetails = this._getRoomDetails.bind(this);
        this.authenticateSpotify = this.authenticateSpotify.bind(this);
        this.getCurrentSong = this.getCurrentSong.bind(this);
        this._getRoomDetails();
    }

    _getRoomDetails() {
        fetch("/api/get-room" + "?code=" + this.roomCode)
            .then((response) => {
                if (!response.ok) {
                    this.props.leaveRoomCallback();
                    this.props.history.push("/");
                }
                return response.json();
            }
        ).then((data) => {
            this.setState({
                votesToSkip: data.votes_to_skip,
                guestCanPause: data.guest_can_pause,
                isHost: data.is_host,
            });
            if (this.state.isHost) {
                this.authenticateSpotify();
            }
        });
    }

    authenticateSpotify() {
        fetch('/spotify/is-authenticated')
            .then((response) => response.json())
            .then((data) => {
                this.setState({spotifyAuthenticated: data.status});
                if (!data.status) {
                    fetch("/spotify/get-auth-url")
                        .then((response) => response.json())
                        .then((data) => {
                            window.location.replace(data.url);
                        })
                }
        });
    }

  getCurrentSong() {
    fetch("/spotify/current-song")
      .then((response) => {
        if (!response.ok) {
          return {};
        } else {
          return response;
        }
      })
      .then((data) => {
        this.setState({ song: data });
        console.log(data);
      });
  }
    _leaveThisButtonPress() {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json" },
        };
        fetch("/api/leave-room", requestOptions).then((_response) => {
            this.props.leaveRoomCallback();
            this.props.history.push("/");
        });
    }

    _updateShowsSetting(value) {
        this.setState({
            showsSetting: value,
        });
    }

    _renderSettings() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <CreateRoomPage update={true}
                                    votesToSkip={this.state.votesToSkip}
                                    guestCanPause={this.state.guestCanPause}
                                    roomCode={this.roomCode}
                                    updateCallback={this._getRoomDetails}
                    />
                </Grid>
                <Grid item xs={12} align="center">
                    <Button variant="contained" color="secondary" onClick={() => this._updateShowsSetting(false)} >
                        Close
                    </Button>
                </Grid>
            </Grid>
        );
    }

    _renderSettingsButton() {
        return (
            <Grid item xs={12} align="center">
                <Button variant="contained" color="primary" onClick={() => this._updateShowsSetting(true)} >
                    Settings
                </Button>
            </Grid>
        );
    }
    render() {
        if (this.state.showsSetting) {
            return this._renderSettings()
        }
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center" >
                    <Typography variant="h4" component="h4">
                        Code: {this.roomCode}
                    </Typography>
                </Grid>
                {this.state.song}
                {this.state.isHost ? this._renderSettingsButton() : null}
                <Grid item xs={12} align="center">
                    <Button variant="contained" color="secondary" onClick={this._leaveThisButtonPress}>
                        Leave Room
                    </Button>
                </Grid>
            </Grid>
        )
    }
}
