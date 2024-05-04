
import { Skeleton } from "@mui/material";

/**
 * ProjectSkeleton is a functional component that represents a skeleton screen for the project component.
 * Skeleton screens are used to indicate to the user that content is loading.
 * 
 */

function ProjectSkeleton() {

    return (
        <>
            <div>
                <Skeleton variant="rectangular" width={"20vw"} height={"30vh"}/>
            </div>
            <div>
                <Skeleton variant="rectangular" width={"20vw"} height={"30vh"}/>
            </div>
        </>
        
    )
}

export default ProjectSkeleton