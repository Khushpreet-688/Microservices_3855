import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStatus() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [status, setStats] = useState({});
    const [error, setError] = useState(null);

	const getStats = () => {
	
        fetch(`http://kafka-acit3855.canadacentral.cloudapp.azure.com/health_check/status`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Service Statuses")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Health Check</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Services Health Checks</th>
						</tr>
						<tr>
							<td colspan="2"><b>Receiver:</b> {status['receiver']}</td>
						</tr>
						<tr>
							<td colspan="2"><b>Storage:</b> {status['storage']}</td>
						</tr>
                        <tr>
							<td colspan="2"><b>Processing:</b> {status['processing']}</td>
						</tr>
                        <tr>
							<td colspan="2"><b>Audit:</b> {status['audit_log']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {status['last_updated']}</h3>

            </div>
        )
    }
}