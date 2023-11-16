document.querySelectorAll('.play-song').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const songId = this.getAttribute('data-song-id');
        playSong(songId);
    });
});

function playSong(songId) {
    fetch(`/get_song/${songId}`)
        .then(response => response.blob())
        .then(blob => {
            const audioPlayer = document.getElementById('audio-player');
            const objectURL = URL.createObjectURL(blob);
            const newSource = document.createElement('source');
            newSource.src = objectURL;
            newSource.type = 'audio/mpeg';
            while (audioPlayer.firstChild) {
                audioPlayer.removeChild(audioPlayer.firstChild);
            }
            audioPlayer.appendChild(newSource);
            audioPlayer.play();

            const songName = document.querySelector(`[data-song-id="${songId}"]`).getAttribute('data-song-name');
            console.log("Song Name:", songName);
            const songNameDisplay = document.getElementById('songNameDisplay');
            songNameDisplay.textContent = `${songName}`;

            fetch(`/album_cover/${songId}`)
                .then(response => response.blob())
                .then(coverBlob => {
                    const songCoverDisplay = document.getElementById('songCoverDisplay');
                    const coverObjectURL = URL.createObjectURL(coverBlob);
                    songCoverDisplay.src = coverObjectURL;
                });
        });
}