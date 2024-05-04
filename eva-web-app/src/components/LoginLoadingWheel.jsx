
import { CircularProgress } from "@mui/material"
import {  blueGrey, amber } from '@mui/material/colors';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import './LoginLoadingWheel.css'

const theme = createTheme({
    palette: {
        primary: amber,
        secondary: blueGrey,
    },
  })

function LoadingWheel({text}) {
    return (
            <div className="wheel-container">
                <ThemeProvider theme={theme}>
                    <CircularProgress 
                    size='8vw'
                    color="secondary"/>
                </ThemeProvider>
                <p className="loading-text">{text}</p>
            </div>
            
    )
}

export default LoadingWheel