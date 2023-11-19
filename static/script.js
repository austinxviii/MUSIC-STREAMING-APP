document.querySelectorAll('.play-song').forEach(link => {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const songId = this.getAttribute('data-song-id');
        playSong(songId);
    });
    const ellipsisIcon = link.querySelector('.fa-ellipsis-h');
    const plusIcon = link.querySelector('.fa-plus');
    if (ellipsisIcon) {
        ellipsisIcon.addEventListener('click', function(event) {
            event.stopPropagation();
            console.log('Ellipsis icon clicked');
        });
    }
    if (plusIcon) {
        plusIcon.addEventListener('click', function(event) {
            event.stopPropagation(); 
            console.log('Plus icon clicked');
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

            // Fetch and update song creator
            const creatorName = document.querySelector(`[data-song-id="${songId}"]`).getAttribute('data-song-creator');
            const creatorNameDisplay = document.getElementById('creatorNameDisplay');
            creatorNameDisplay.textContent = creatorName;

            fetch(`/album_cover/${songId}`)
                .then(response => response.blob())
                .then(coverBlob => {
                    const songCoverDisplay = document.getElementById('songCoverDisplay');
                    const coverObjectURL = URL.createObjectURL(coverBlob);
                    songCoverDisplay.src = coverObjectURL;
                });
        });
}
