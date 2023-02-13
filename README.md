<h1 align="center">
<img src="/ShotSpotter.svg" width="600">
</h1>

# Source Localization with ShotSpotter Audio

Software for working with audio files produced by the ShotSpottter Respond gunshot location system. It is complementary code to the paper "Determining the Source Location of Gunshots From DigitalRecordings." The purpose of this repo is to make plain the information embedded in ShotSpotter WAV files and to demonstrate how they can be used to produce a multilateration solution.

After downloading this repo, the primary usage is as follows:

```  
python src/find_pulses.py "/path/to/ShotSpotter/wav/folder/"  
```

This will walk you through the whole process of what this repo has to offer. It will open the wav files for you and prompt you for the sample number of the start of the shot impulse. You may only do one shot at a time with the current implementation. After entering nothing or a sample start number for each .wav file, the code will output a json file containing the pulse objects necessary to produce a multilateration and the multilateration solution for the data entered.

You may inspect the smj object of a ShotSpotter WAV file with:

```   
python src/smjx_reader.py "/path/to/ShotSpotter/wav/file/0123456789abcdef0123456789abcdef01234567.wav"  
```

Or compute a location with a find_pulses.py style json file using the following:

```
python src/find_location.py "/path/to/find_pulses/json/file/0123456789abcdef0123456789abcdef.json"  
```

## Dependencies
- [NumPy](https://www.numpy.org)
- [Python](https://www.python.org/) >= 3.7
- [Audacity](https://www.audacityteam.org/)

## Contributors
- Zac Plett
- Scott Lamkin
- Robert B. Calhoun
- Murphey Johnson
- Contributors to the [Python utm project](https://github.com/Turbo87/utm)