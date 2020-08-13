### required_files
Simple but effective checking if externals are present.

Small sample:

#### Check if `java` is present?
```
from required_files import RequiredCommand
 
java_exe = RequiredCommand('java').check()
```


#### Check if a certain file is present in bin?
In this example it's a bit silly as you normally would do this via pip, but I intend to show
  you how to use it in order to download and extract zip files transparently.
For example I use this in my own projects to download binaries in case they're not present on the target
  system. This way maintenance becomes very easy and I can always run it everywhere. 
```
from required_files import RequiredLatestGithubZipFile
 
extracted_dir = RequiredLatestGithubZipFile(
    'https://github.com/svaningelgem/required_files/releases/latest',
    'bin',
    'bin/required_files/required_files.py'
).check()
```

This piece of code will check if `bin/required_files/required_files.py` is present.
If it's not, it will download the latest zip release from github from the mentioned url, and extract it.

If the optional parameter `skip_initial_dir` is set to False, it will extract as-is. The default will check
  if there is an initial directory and skip that one.

An example to clarify this parameter. Assume we have a zip with the following contents:
- dir1 / 
- dir1 / testfile.txt
- dir1 / dir2 /
- dir1 / dir2 / testfile.txt

As you can see, everything is located under 'dir1'. So if you leave the default of `skip_initial_dir` as True,
  the module will extract it as (see next list) under the `bin` directory (as per the example above):
- testfile.txt
- dir2 / testfile.txt


#### Other classes available:
- `RequiredCommand`(`command`)
- `RequiredFile`(`url`, `target_filename`)
- `RequiredZipFile`(`url`, `target_directory`, `file_to_check`, `skip_initial_dir`)
- `RequiredLatestBitbucketFile`(`url`, `target_directory`, `file_to_check`, `skip_initial_dir`)
- `RequiredLatestGithubZipFile`(`url`, `target_directory`, `file_to_check`, `skip_initial_dir`)
