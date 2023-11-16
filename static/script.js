document.querySelectorAll('.play-song').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const songId = this.getAttribute('data-song-id');
        playSong(songId);
    });
    const ellipsisIcon = link.querySelector('.fa-ellipsis-h');
    if (ellipsisIcon) {
        ellipsisIcon.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent the click event from propagating to the parent (play-song link)
            // Add your ellipsis icon click logic here
            console.log('Ellipsis icon clicked');
        });
    }
});

function playSong(songId) {
    fetch(`/get_song/${songId}`)
        .then(response => response.blob())
        .then(blob => {
            const objectURL = URL.createObjectURL(blob);

            // Create a new audio element
            const newAudioPlayer = document.createElement('audio');
            newAudioPlayer.controls = true;
            newAudioPlayer.autoplay = true;
            newAudioPlayer.name = 'media';
            newAudioPlayer.id = 'audio-player';

            // Create a new source element
            const newSource = document.createElement('source');
            newSource.src = objectURL;
            newSource.type = 'audio/mpeg';

            // Append the new source element to the new audio element
            newAudioPlayer.appendChild(newSource);

            // Replace the old audio element with the new one
            const oldAudioPlayer = document.getElementById('audio-player');
            oldAudioPlayer.parentNode.replaceChild(newAudioPlayer, oldAudioPlayer);

            // Fetch and update song information
            const songName = document.querySelector(`[data-song-id="${songId}"]`).getAttribute('data-song-name');
            const songNameDisplay = document.getElementById('songNameDisplay');
            songNameDisplay.textContent = songName;

            fetch(`/album_cover/${songId}`)
                .then(response => response.blob())
                .then(coverBlob => {
                    const songCoverDisplay = document.getElementById('songCoverDisplay');
                    const coverObjectURL = URL.createObjectURL(coverBlob);
                    songCoverDisplay.src = coverObjectURL;
                });
        });
}
