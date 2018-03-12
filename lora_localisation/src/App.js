import React, { Component } from 'react';
import update from 'immutability-helper';
import {
  Scatter,
  ScatterChart,
  XAxis, YAxis,
  CartesianAxis,
  Legend,
  Tooltip
} from 'recharts';
import openSocket from 'socket.io-client';
import './App.css';
import worldsData from "./worlds.json";

// Material-UI
import Card, { CardContent } from 'material-ui/Card';
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

const socket = openSocket('http://localhost:5000');

class App extends Component {
  constructor() {
    super();
    this.state = {
      nodes: {},
      gateways: {},
      currId: 0,
      world: "floor7labs",
      broadcastRate: 60,
      angle: 0,
      drawerOpen: false,
      antennaDialogOpen: false
    };
  }

  componentDidMount = () => {
    this.populateGateways(this.state.world);
    socket.on('nodeFound', node => {
      this.handleReceivedNode(node);
    });
    socket.on('currIdChange', newCurrId => {
      this.handleCurrIdUpdate(newCurrId);
    });
    setInterval(() => socket.emit('update', this.state.currId), 500);
  }

  handleCurrIdUpdate = newCurrId => this.setState({
    currId: newCurrId
  })

  handleMessageChange = type => event => this.setState({
    [type]: event.target.value
  }, console.log(type, "has been changed to", event.target.value, "."))

  handleReceivedNode = node => this.setState({
    nodes: update(this.state.nodes, {
      [node.NiD]: {
        $set: {
          "lval": node.LVal,
          "lng": node.lng,
          "lat": node.lat
        }
      }
    })
  })

  handleWorldChange = event => this.setState({
    world: event.target.value
  }, () => this.populateGateways(this.state.world))


  populateGateways = worldName => this.setState({
    gateways: worldsData[worldName]
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
            <MenuItem value="floor7labs">7th Floor Computer Labs</MenuItem>
            <MenuItem value="floor9labs">9th Floor Masters' Labs</MenuItem>
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
            style={{ width: `100` }}
          >
            <ChevronRightIcon />
          </IconButton>
          <Divider />
          <Typography variant="title">Nodes</Typography>
          <div style={{ display: `flex`, marginRight: `0.5em`, flexWrap: `wrap`, width: `15em`, flexDirection: `column` }}>
            {Object.keys(this.state.nodes).map(id => (
              <Card key={id} style={{ marginBottom: `0.5em` }}>
                <CardContent>
                  <Typography component="h3">NiD: {id}</Typography>
                  <Typography>LVal: {this.state.nodes[id].lval}</Typography>
                </CardContent>
              </Card>
            ))}
          </div>
        </Drawer>
      </Hidden>
      <ScatterChart width={1200} height={700}>
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