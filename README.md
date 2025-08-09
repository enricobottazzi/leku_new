# leku_new

### How to add a blogpost

1. Write the blogpost in markdown format and add it inside the `md` folder. For example, `md/example.md`. Make sure that all your latex format are inside `$` or `$$` for inline and block latex respectively. 
2. Run `python3 generate_post.py posts/example.md posts/output.html` to generate a HTML file with proper latex formatting.
3. Duplicate the `post_template.html` file and rename it to `your_title.html`.
4. Copy the content of `output.html` into the `<div class="content">` class of `your_title.html`.
5. Add your post inside the `<ul class="posts" id="posts-list">` in `index.html` with the correct date and title
6. Double check the correctness of the newly added blogpost:
    - Check the links
    - Check the images (these are not automatically imported from HackMD)
    - Check the Latex formatting
7. Delete the `output.html` file and the original markdown file.