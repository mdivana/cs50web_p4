function editPost(id) {
    var edit_box = document.querySelector(`#edit-box`);
    var edit_btn = document.querySelector(`#edit-btn`);
    var edit_area = document.querySelector(`#content`);
    edit_area.style.display = 'none';
    edit_box.style.display = 'block';
    edit_btn.style.display = 'block';

    edit_btn.addEventListener('click', () => {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
        fetch(`/edit/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                content: edit_box.value
            })
        })
        .then(response => {
            if (response.ok) {
                // Update the post content on success
                const postContentElement = document.querySelector(`.article-content`);
                if (postContentElement) {
                    postContentElement.textContent = edit_box.value;
                    edit_area.style.display = 'block'
                    edit_box.style.display = 'none';
                    edit_btn.style.display = 'none';
                } else {
                    console.error(`Error: Post content element with ID 'post-${id}' not found.`);
                }
            } else {
                console.error('Error updating post content');
            }
        })
        .catch(error => {
            console.error('Error updating post content:', error);
        });
    }); 
}

    function like(id) {
        var like_btn = document.querySelector(`#like-btn-${id}`);
        var like_count = document.querySelector(`#like-count-${id}`);
        
        if (like_btn.textContent === 'Like') {
            fetch('/like/' + id, {
                method: 'PUT',
                body: JSON.stringify({
                    likes: 1,
                })
            })
            .then(() => {
                like_btn.textContent = 'Unlike';
                return fetch('/like/' + id);
            })
            .then((response) => response.json())
            .then(post => {
                like_count.innerHTML = "Likes: " + post.likes;
            });
        } else {
            fetch('/like/' + id, {
                method: 'PUT',
                body: JSON.stringify({
                    likes: 0,
                })
            })
            .then(() => {
                like_btn.textContent = 'Like';
                return fetch('/like/' + id);
            })
            .then((response) => response.json())
            .then(post => {
                like_count.innerHTML = "Likes: " + post.likes;
            });
        }
        return false;
    }