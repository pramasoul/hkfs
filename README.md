# hkfs
Hash key file system. For archiving when duplicate files are expected.


## Motivation
All those backup folders, copies of old machines, safety archive of important stuff,
media duplicated across machines that are then backed up or archived. Exponential
disk inflation.

## Objectives
* Keep only one copy of the data
* Find subtrees that are duplicated somewhere else
** Allows safe pruning, knowing that the contents are duplicated (referenced) elsewhere
* Never lose data
* Never lose metadata
* Make backup of the archive straightforward and efficient

## Approach
* Use hard links
* Hash file contents
* Maintain a directory tree of all the files, named by hash value
* Prevent changing file contents
* Maintain a directory tree of human-readable names
** from the ingest names, as subsequently rearranged and altered

## Operations
* Ingest from directory tree
* Ingest from tar archive
* Consistency checks
** Verify hash corresponds to file path
** Verify human-readable directory tree files are all linked in
* Find other instances of a file by contents (hash)
* Find files in a directory tree that are not also somewhere else
* Find the orphan hash tree files (ones no longer referenced in the human-readable tree)
* Backup the archive
