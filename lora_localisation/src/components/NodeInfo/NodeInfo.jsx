import React from 'react';

// Material-UI
import Typography from 'material-ui/Typography';
import Card, { CardContent } from 'material-ui/Card';
import { LinearProgress } from 'material-ui/Progress';

const MAX_LIGHT_VAL = 512 // TODO: Actual value is 4096, change during actual use.

const brightnessValue = lightValue => (lightValue / MAX_LIGHT_VAL) * 100;

export default (props) => (
    <Card>
        <CardContent>
            <Typography variant="title">{props.nodeID}</Typography>
            <Typography component="p">Brightness: {props.lightVal}</Typography>
            <LinearProgress
                variant="buffer"
                value={brightnessValue(props.lightVal)}
                valueBuffer={MAX_LIGHT_VAL}
                color="secondary"
            />
            <p>{props.location.lng}, {props.location.lat}</p>
        </CardContent>
    </Card>
)