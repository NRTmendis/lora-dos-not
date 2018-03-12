import React from 'react';

// Material-UI
import Button from 'material-ui/Button';
import TextField from 'material-ui/TextField';
import Typography from 'material-ui/Typography';
import Dialog, {
    DialogTitle,
    DialogActions,
    DialogContent,
    DialogContentText
} from 'material-ui/Dialog';
import { Divider } from 'material-ui/Divider';
// import Icon from 'material-ui/Icon';

const styles = {
    msgContainer: {
        display: `flex`,
        flexDirection: `column`
    }
}

export default (props) => (
    <Dialog
        open={props.dialogOpen}
        onClose={props.handleDialog}
    >
        <DialogTitle>Update Gateway Parameters</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Update the broadcast rate or angle or a a gateway through the MQTT server.
            </DialogContentText>
            <TextField
                id="gateway"
                label="Gateway"
                value={"All"}
                disabled
            />
            <TextField
                id="broadcastRate"
                label="Broadcast rate"
                value={props.initValues.broadcastRate}
                type="number"
                onChange={props.handleMessageChange('broadcastRate')}
            />
            <TextField
                id="angle"
                label="Angle"
                value={props.initValues.angle}
                type="number"
                onChange={props.handleMessageChange('angle')}
            />
        </DialogContent>
        <DialogActions>
            <Button color="secondary" onClick={props.handleDialog}>
                Cancel
            </Button>
            <Button color="primary" onClick={props.sendMessageJSON}>
                {/* <Icon>send</Icon> */}
                Send
            </Button>
        </DialogActions>
    </Dialog>
)