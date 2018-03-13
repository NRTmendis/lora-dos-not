import React from 'react';

// Material-UI
import Button from 'material-ui/Button';
import TextField from 'material-ui/TextField';
import Dialog, {
    DialogTitle,
    DialogActions,
    DialogContent,
    DialogContentText
} from 'material-ui/Dialog';
// import Icon from 'material-ui/Icon';

const styles = {
    msgContainer: {
        display: `flex`,
        flexDirection: `column`,
        marginBottom: `0.5em`
    }
}

export default (props) => (
    <Dialog
        open={props.dialogOpen}
        onClose={props.handleDialog}
    >
        <DialogTitle>Update Gateway Parameters</DialogTitle>
        <DialogContent style={styles.msgContainer}>
            <DialogContentText>
                Update the broadcast rate or angle of a gateway through the MQTT server.
            </DialogContentText>
            <TextField
                id="gateway"
                label="Gateway - All"
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