import {Fragment} from 'react';
import styles from './Overlay.css';

export function Overlay({ isOpen, children }) {
    return (
        <Fragment>
        {isOpen && <div className={styles.overlay} />}
        {children}
        </Fragment>
    );
    }

export default Overlay;