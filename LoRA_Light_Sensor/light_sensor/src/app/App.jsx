import React, { Component } from 'react';
sqlite3 = require('better-sqlite3');

const MAX_LVAL = 255

const cardDisplayStyle = {
    padding: `0`,
    margin: `0`,
    display: `flex`,
    flexWrap: `wrap`,
    justifyContent: `center`,
}

const cardStyle = {
    backgroundColor: `black`,
    color: `white`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    justifyContent: `center`,
    width: `20em`,
    margin: `1em`,
    padding: `1em`,
    borderRadius: `0.5em`
}

const meterStyle = {
    width: `100%`
}

let dummyData = [
    {
        "key": 1,
        "NiD": "240AC4026ACC",
        "LVal": 155
    },
    {
        "key": 2,
        "NiD": "240AC4026ACD",
        "LVal": 108
    },
    {
        "key": 3,
        "NiD": "240AC4026ACE",
        "LVal": 238
    },
    {
        "key": 4,
        "NiD": "240AC4026ACF",
        "LVal": 67
    }
]

class IndicatorCard extends Component {
    constructor(props) {
        super(props);
        this.state = {
            "light": this.props.NiD,
            "lval": this.props.LVal
        }
        this.updateBrightness = this.updateBrightness.bind(this);
    }

    updateBrightness(event) {
        if (event.target.value !== "") {
            this.setState({
                lval: event.target.value
            })
        }
    }

    render() {
        return (
            <div style={cardStyle}>
                <p>Light: {this.state.light}</p>
                <p>Brightness: {this.state.lval}</p>
                <meter style={meterStyle} max={MAX_LVAL} min={0.0} high={0.9} low={0.1} value={this.state.lval}></meter>
                <input type="range" min={0.0} max={MAX_LVAL} value={this.state.lval} onChange={this.updateBrightness} />
            </div>
        )
    }
}

const App = () => {
    return (
        <div style={{ padding: `1em` }}>
            <h1>Active Lights</h1>
            <div style={cardDisplayStyle} >
                {dummyData.map(light =>
                    <IndicatorCard key={light.key} NiD={light.NiD} LVal={light.LVal} />
                )}
            </div>
        </div>
    )
}

export default App;