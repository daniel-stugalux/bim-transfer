import React from 'react';
import Dialog from '@material-ui/core/Dialog';
import GifTutorial from '../media/tutorial_gif.gif';


const GifDialog = (props) => {
    const { onClose, open } = props;

    return (
        <Dialog onClose={onClose} aria-labelledby="tutorial-gif-dialog" open={open}>
            <img src={GifTutorial} alt="tutorial" />
        </Dialog>
    )
};

export default GifDialog;