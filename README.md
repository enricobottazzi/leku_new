# leku_new

`open index.html` to view the blog.

### How to add a blogpost

1. Write the blogpost in markdown format and add it inside the `md` folder. For example, `md/example.md`. Make sure that all your LaTeX is inside `$` or `$$` for inline and block math respectively. The title is extracted from the first `# heading` in the file. Any image file should be added to the `assets` folder.

2. Run the generator:

   ```bash
   python3 generate_post.py md/example.md --date 2026-02-10
   ```

   Omit `--date` to use today's date. 

3. Double check the result by running `open index.html` and verifying in the browser:
   - Title, date are correct both in the index.html and the post.html files
   - Links are correct
   - Images render correctly
   - LaTeX formatting
   - Code blocks and blockquotes
   - It doesn't overflow on mobile 