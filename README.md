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
* Fast

## Approach
* Use hard links
* Hash file contents
** use blake3
* Maintain a directory tree of all the files, named by hash value
* Prevent changing file contents
* Maintain a directory tree of human-readable names
** from the ingest names, as subsequently rearranged and altered
* Make it easy to find files and subtrees that are duplicated elsewhere
** Useful: file stat gives number of hard links to inode
** Useful: depth-first subtree walk can construct a hash-of-hashes to represent a directory node
*** Wherever those match, the subtrees match as to file contents and tree structure (not necessarily permissions)
*** Want an efficient way to associate an inode with a hash, as well as a hash with an inode


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

### Internal Functions
*


## Databases
* File contents from hash key
** In the filesystem, in a subtree with names constructed from the hash values
*** viz. LJ in lj.py
* Hash from inode
** Use: associating hashes to nodes of archive file tree
** Construct or re-construct by scan of hash subtree
*** Or can re-hash the inode contents
** Update with assimilations
** Remove deletions
* File paths from inode
** Construct or re-construct by scan of archive subtree
** Update with assimilations
** Update with deletions

# Hints
* os.stat(f.fileno())
* sqlite is safe with multiple processes if used right, viz. https://rbranson.medium.com/sharing-sqlite-databases-across-containers-is-surprisingly-brilliant-bacb8d753054

## Questions
* What window bugs arise
