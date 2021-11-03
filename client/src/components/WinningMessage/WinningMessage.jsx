import React from 'react'
import Card from "@material-ui/core/Card";
import { CardContent } from '@material-ui/core';
import Typography from "@material-ui/core/Typography";

const WinningMessage = ({messages}) => {

    console.log(messages)
    const hideMessage = messages.length === 0
    console.log(hideMessage)

    if (hideMessage) {
        return (<div></div>)
    } else {
        return (
            <div>
            {messages.map(message => (
                <Card className="winning-message-card">
                    <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                            {message}
                        </Typography>
                    </CardContent>
                </Card>
            ))
            }
            </div>
             
          )
    }
}

export default WinningMessage