import React, { Component } from 'react';
import update from 'immutability-helper';
// Recharts
import {
  Scatter,
  ScatterChart,
  XAxis, YAxis,
  CartesianAxis,
  Legend,
  Tooltip
} from 'recharts';

// Victory (Formidable)
// import {
//   VictoryChart,
//   VictoryScatter,
// } from 'victory';

import openSocket from 'socket.io-client';
import './App.css';
import worldsData from "./worlds.json"

// Material-UI
import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import 'typeface-roboto'
import Typography from 'material-ui/Typography';
import { MenuItem } from 'material-ui/Menu';
import Select from 'material-ui/Select';
import Paper from 'material-ui/Paper';
import Drawer from 'material-ui/Drawer';
import MenuIcon from 'material-ui-icons/Menu';
import SettingsInputAntennaIcon from 'material-ui-icons/SettingsInputAntenna';
import IconButton from 'material-ui/IconButton';
import Hidden from 'material-ui/Hidden';
import ChevronRightIcon from 'material-ui-icons/ChevronRight';
import Divider from 'material-ui/Divider';

// Components
import MessageInterface from './components/MessageInterface/MessageInterface';
import NodeInfo from './components/NodeInfo/NodeInfo';

const socket = openSocket('http://localhost:5000');

class App extends Component {
  constructor() {
    super();
    this.state = {
      nodes: {},
      gateways: {},
      world: "floor7labs",
      broadcastRate: 60,
      angle: 0,
      drawerOpen: true,
      antennaDialogOpen: false
    };
  }

  componentDidMount = () => {
    this.populateGateways(this.state.world);
    socket.on('nodeUpdate', newNodes => this.setState({
      nodes: update(this.state.nodes, {
        $set: newNodes
      })
    }))
    setInterval(() => socket.emit('update'), 500);
  }

  handleCurrIdUpdate = newCurrId => this.setState({
    currId: newCurrId
  })

  handleMessageChange = type => event => this.setState({
    [type]: event.target.value
  }, console.log(type, "has been changed to", event.target.value, "."))

  handleWorldChange = event => this.setState({
    world: event.target.value
  }, () => this.populateGateways(this.state.world))

  // populateGateways = worldName => fetch('../../worlds.json', {
  //   headers: {
  //     'content-type': 'application/json'
  //   },
  // })
  //   .then(response => response.text())
  //   .then(json => console.log(json))

  populateGateways = worldName => this.setState({
    gateways: worldsData[worldName].gateways
  })

  sendMessageJSON = () => socket.emit('gatewayUpdate', JSON.stringify({
    broadcastRate: this.state.broadcastRate,
    angle: this.state.angle
  }))

  handleDrawer = () => this.setState(prevState => ({
    drawerOpen: !prevState.drawerOpen
  }))

  handleAntennaDialog = () => this.setState(prevState => ({
    antennaDialogOpen: !prevState.antennaDialogOpen
  }))

  render = () => (
    <Paper elevation={0} className="App">
      <AppBar position="static" color="default" style={{ boxShadow: `none` }}>
        <Toolbar style={{ display: `flex`, justifyContent: `space-between` }}>
          <Typography variant="title" color="inherit">Control Panel</Typography>
          <Select
            value={this.state.world}
            onChange={this.handleWorldChange}
            ref={node => (this.worldSelector = node)}
          >
            {Object.keys(worldsData).map(world => (
              <MenuItem key={world} value={world}>{worldsData[world].name}</MenuItem>
            ))}
          </Select>
          <IconButton
            color="inherit"
            onClick={this.handleAntennaDialog}
          >
            <SettingsInputAntennaIcon />
          </IconButton>
          <IconButton
            color="inherit"
            onClick={this.handleDrawer}
          >
            <MenuIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Hidden>
        <Drawer
          color="default"
          variant="persistent"
          anchor="right"
          open={this.state.drawerOpen}
          onClose={this.handleDrawer}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
        >
          <IconButton
            onClick={this.handleDrawer}
            style={{ width: `100%`, height: `8%` }}
          // TODO: Height currently a hack, add theme.mixins.toolbar + withStyles
          >
            <Typography variant="title">Nodes</Typography>
            <ChevronRightIcon />
          </IconButton>
          <Divider />
          <div style={{ display: `flex`, flexWrap: `wrap`, width: `15em`, flexDirection: `column` }}>
            {Object.keys(this.state.nodes).map(id => (
              <NodeInfo
                key={id}
                nodeID={id}
                lightVal={this.state.nodes[id].lightVal}
                location={{
                  lat: this.state.nodes[id].lat,
                  lng: this.state.nodes[id].lng
                }}
              />
            ))}
          </div>
        </Drawer>
      </Hidden>
      {/* <VictoryChart size={2}>
        <VictoryScatter
          data={Object.values(this.state.gateways)}
          x="lng"
          y="lat"
        />
        <VictoryScatter
          data={Object.values(this.state.nodes)}
          size={2}
          style={{ data: { fill: `red` } }}
          x="lng"
          y="lat"
        />
      </VictoryChart> */}
      <ScatterChart width={1150} height={700}>
        <CartesianAxis strokeDasharray="3 3" />
        <XAxis dataKey={"lng"} type="number" name="lng" unit="m" />
        <YAxis dataKey={"lat"} type="number" name="lat" unit="m" />
        <Scatter name="gateways" data={Object.values(this.state.gateways)} fill="#000" />
        <Scatter name="nodes" data={Object.values(this.state.nodes)} fill="red" />
        <Legend />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
      </ScatterChart>
      <MessageInterface
        dialogOpen={this.state.antennaDialogOpen}
        handleMessageChange={this.handleMessageChange}
        handleDialog={this.handleAntennaDialog}
        initValues={{
          broadcastRate: this.state.broadcastRate,
          angle: this.state.angle
        }}
        sendMessageJSON={this.sendMessageJSON}
      />
    </Paper>
  )
}

export default App;