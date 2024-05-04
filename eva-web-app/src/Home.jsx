import { useLocation } from 'react-router-dom';

function Home() {
  const location = useLocation();
  const { username } = location.state || { username: 'Guest' };

  return (
    <h2>Welcome {username}</h2>
  );
}

export default Home;
