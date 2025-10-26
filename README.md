# leku_new

### How to add a blogpost

1. Write the blogpost in markdown format and add it inside the `md` folder. For example, `md/example.md`. Make sure that all your latex format are inside `$` or `$$` for inline and block latex respectively. 
2. Run `python3 generate_post.py md/example.md md/output.html` to generate a HTML file with proper latex formatting.
3. Duplicate the `blog_placeholder.html` file and rename it to `your_title.html`.
4. Copy the content of `output.html` into the `<section class="post-content">` class of `your_title.html`. Update `title`, `post-title` and `post-date`.
5. Add your post inside the `<ul class="posts" id="posts-list">` in `index.html` pointing to the correctly file, with the correct date and title
6. Double check the correctness of the newly added blogpost:
    - Check the links
    - Check the images (these are not automatically imported from HackMD)
    - Check the Latex formatting
7. Delete the `output.html` file.