-- Use folder name to build extension name and tag.
local ext = get_current_extension_info()

project_ext (ext)

repo_build.prebuild_link { "msft", ext.target_dir.."/msft" }