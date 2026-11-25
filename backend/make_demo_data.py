import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"

TEXTS = {
1: """
i have a big exam tomorrow and i am nervous
can you share your notes from the last class
the library closes early today so i will go now
i am going to the canteen to get some tea
our teacher gave us a new assignment for friday
do you want to study together after lunch today
i forgot my notebook in the hostel room again
the exam starts at ten so please come early
i need to finish my project report tonight
can we meet at the library after the class
i did not understand the last chapter at all
the lecture was so long and a little boring
please send me the question paper from last year
i am going to sleep early before the test
my friend is helping me with the math homework
we have a group presentation next week in class
i will bring the books to the hostel tomorrow
the results will come out on monday morning
i hope i pass the exam this time
do you know when the next class starts today
i left my charger in the classroom yesterday evening
the teacher said the test will be very easy
i am so tired after studying all night long
can you save a seat for me in class
i need some help with the science project today
the canteen food was good today and very cheap
let us go to the library and read together
i will call you after my class is over
our college is organizing a sports day next month
i am writing my essay for the english class
please remind me about the assignment on thursday morning
the hostel wifi is not working since last night
i got good marks in the last exam
we should start preparing for the final exam soon
thank you so much for your help with homework
""",
2: """
the new match starts in five minutes get ready
i am stuck in ranked and the lag is terrible
can you join my squad for the tournament tonight
we lost the last round because of bad teamwork
i will stream my gameplay after dinner today
my ping is so high i cannot even move
let us play one more match before we sleep
who is carrying the team in the next game
i just got a new headset and it sounds amazing
the server was down for an hour this morning
please wait for me i am still downloading the update
that was an amazing shot did you see it
i will buy the new skin when it comes out
our team won the final and everyone was so happy
can you invite me to the party before we start
i need a better graphics card for this game
the boss fight was really hard but we finished
do not forget to charge your controller before the game
i am going to practice aim for one hour
the new map looks great but the loading is slow
we need one more player for the ranked match
turn on your microphone so we can talk strategy
i played the whole night and now i am sleepy
my friend gave me his old keyboard for free
let us watch the finals together on the stream
i keep losing the first round every single time
can you teach me how to play this character
the update fixed the bug but made a new one
i will be online in ten minutes with the team
that last move was a total disaster for us
we should change our strategy for the next match
the tournament prize is big so we must win
i got a new high score in the game
do you want to play with me tonight
good game everyone see you all in the next match
""",
3: """
i am making dal and rice for dinner tonight
can you buy some fresh vegetables from the market
the soup needs a little more salt and pepper
i will bake a cake for her birthday tomorrow
please wash the rice before you put it on
we ran out of cooking oil again this week
the kitchen smells so good right now
i am trying a new recipe for the evening
do you want tea with milk or without sugar
add the onions first and then the tomatoes slowly
the bread is still warm come and eat now
she loves my spicy chicken curry every single time
i need more garlic and ginger for the sauce
let me cook breakfast before you leave for work
the pan was too hot and the food burned
i will prepare lunch for everyone at noon today
can you pass me the big spoon please
we should invite them over for dinner this weekend
the potatoes need ten more minutes on the stove
i like my coffee strong with a little sugar
please keep the leftover food in the fridge tonight
this recipe needs fresh herbs and lemon juice today
i am making sweet rice pudding for the festival
the oven is ready so put the tray inside
do not forget to turn off the gas
i bought fresh fish from the market this morning
can you taste the soup and tell me
dinner will be ready in half an hour
the kids asked for noodles again tonight
i will fry the eggs and make some toast
she gave me a great recipe for pickle
we need milk and butter for the morning
the whole house smells like fresh baked bread
i cooked too much food so come and eat
thank you for helping me in the kitchen today
""",
4: """
i pushed the new code to the main branch
there is a bug in the login page again
can you review my pull request before the meeting
the server crashed last night and nobody noticed it
i will deploy the update after lunch today
the database is slow and we need to fix
please check the logs and tell me the error
i am writing tests for the new feature now
the build failed because of a missing package again
let us discuss the design in the morning meeting
i fixed the issue but the test still fails
can you restart the server and try once more
the api returns an error when the token expires
i need more time to finish this task properly
we should add a cache to speed things up
my laptop is slow when i compile the project
the client wants one more change before the release
i will update the documentation after the code review
do not merge the branch before the tests pass
the new version is live and working fine
i found the problem it was a small typo
please send me the error message from the console
we need to upgrade the library to the latest version
the frontend and backend are finally working together now
i will write a script to automate this work
can you help me debug this function today
the app is crashing on the old phones
our team is working on a big release this month
let me check the code and call you back
the deadline is tomorrow so we must hurry up
i learned a new trick for faster database queries
the pipeline is green and ready to deploy
someone broke the build and now everyone is waiting
i spent the whole day fixing one bug
good job team the release went smoothly today
""",
5: """
i am going to the gym at six
today is leg day and i am already tired
can you be my workout partner this evening
i ran five kilometers this morning before work
drink more water and eat enough protein every day
my muscles are so sore after yesterday
let us start with a short warm up first
i want to lose weight before the summer
the gym was crowded so i did cardio
do you want to join me for a run
i bought a new pair of running shoes
rest day today so i will only stretch
i am trying to sleep eight hours every night
the trainer showed me a new exercise today
we should do yoga in the morning together
i lifted heavier weights today and felt really strong
please remind me to take my protein shake
my goal is to run a marathon someday
i skipped the gym yesterday and feel guilty
can you count my reps while i lift
the morning walk by the lake was so peaceful
i need to eat healthy food this whole week
let us do pushups and squats before breakfast
my fitness app says i walked ten thousand steps
the gym closes at nine so come early
i feel great after a long hard workout
do not forget your water bottle and towel
i am training for a cycling race next month
she runs faster than me every single time
we will start the new workout plan on monday
i need a rest because my knee hurts
let us meet at the park for jogging
the best part of the day is exercise
i finally finished the thirty day fitness challenge today
thank you for pushing me to work harder
""",
6: """
we are planning a trip to the mountains next month
the bus leaves at five in the morning
i booked a hotel near the lake already
can you check the weather before we start
i packed my bag and camera for the trek
the view from the top was absolutely beautiful
our flight is delayed by two hours again
let us rent a bike and explore the city
do you have the tickets for the train
the local food here is so tasty and cheap
i want to visit the old temple tomorrow
we reached the hotel late at night yesterday
the road was bumpy but the scenery was amazing
please keep your passport and money in a safe place
i met some friendly people on the bus today
the sunrise at the hill was worth waking early
can you take a photo of me here
we should start walking before it gets too hot
the guide told us a great story about the village
i lost my map and now we are lost
this is the best trip i have ever taken
we will camp near the river tonight
do not forget to carry warm clothes for the night
the market here sells beautiful handmade bags and scarves
i am so excited for the next adventure
our taxi is waiting outside the hotel right now
the trail was steep but we made it
i will send you pictures when we reach the top
let us try the famous street food tonight
the weather turned cold and it started to rain
we missed the last bus and walked home
can you book two tickets for the morning train
the lake looks like a mirror at sunrise
i want to travel to a new place every year
safe travels and see you after the trip
""",
7: """
the kids are asleep so we can talk now
please help her with the homework after dinner
i need to pick up the children from school
he has a fever so i kept him home
can you buy milk and some fruits for the kids
the school called me about the parents meeting tomorrow
it is bedtime so please brush your teeth now
she drew a beautiful picture for her grandmother today
do not forget the lunch box and the water bottle
our son won first prize in the drawing competition
i will take them to the park this evening
the baby woke up three times last night
please turn off the television and finish your homework
he does not want to eat his vegetables again
we are going to visit grandma this weekend
the teacher said she is doing very well
can you read a story to the little one
i signed the school form and put it inside
the kids are playing outside so be careful
i am so proud of how well they behave
let us make a cake for his birthday party
she lost her tooth and was so excited
the school bus comes at seven so wake them
i need a quiet hour to relax tonight
they have exams next week so no games
please put the toys back in the box
he learned to ride a bike today by himself
the doctor said the baby is healthy and strong
we should plan something special for the holidays
i packed their bags for the school trip
she asked me a hundred questions about the moon
can you help me clean up the room
the kids love when we cook together on weekends
i hope they sleep well tonight and stay warm
thank you for taking care of the children today
""",
8: """
the shop opens at eight and closes at nine
we ran out of sugar and rice today
the new stock will arrive on tuesday morning
how much is this shirt in the window
i can give you a good price today
the customer wants a discount on the big order
please count the money before you close the shop
our delivery boy is late with the packages again
the price of onions went up this week
can you put these boxes on the top shelf
we have a sale on shoes this weekend
the supplier called and said the truck is coming
i need to order more soap and biscuits
she paid with a card so please check
the shop was very busy during the festival
do you have change for a big note
let me write the bill and give you receipt
we should clean the shop before the customers come
i sold everything in the morning and went home
the market is slow today because of the rain
please keep the best items near the front
he asked me to hold the order until friday
the new brand sells really fast in our area
can you update the price list on the board
i gave him a free gift for being loyal
we need a bigger fridge for the cold drinks
the owner wants a report of this month sales
do not forget to lock the door and lights
our customers love the fresh bread every morning
i will call the supplier about the broken boxes
business was good this month and we made profit
please pack the items carefully so nothing breaks
the shop next door is selling cheaper than us
i will open early tomorrow for the morning rush
thank you for shopping with us come again
""",
9: """
my shift starts at seven and ends at three
the patient in room four needs more rest
please check the blood pressure of the next patient
the doctor will visit the ward after lunch
i was on night duty and now sleepy
can you bring some water for the old man
the medicine must be given every eight hours
i am so tired after a long shift
the new nurse is learning very fast
please write the report before you leave the ward
the family is waiting outside to meet the doctor
he is feeling better and can go home tomorrow
we have a busy day because of the emergency
please wash your hands before touching the patient again
the clinic opens early so patients come in time
i gave her the injection and she was brave
can you help me move the patient to bed
the lab results will come this afternoon for sure
the baby is healthy and the mother is happy
i need a break after the morning round
our hospital needs more beds and more staff
the doctor asked me to call the family
please keep the ward quiet because patients are sleeping
i am studying for my nursing exam next month
we cleaned the room and changed all the sheets
the old lady always thanks me with a smile
can you cover my shift on saturday morning
the pharmacy is out of that medicine today
she is recovering well and eating more now
i hope the patient will sleep well tonight
the new machine helps us check the heart
please remind him to take his medicine after food
we had a calm night and everyone slept
i love my work even when it is hard
good morning team let us start the round
""",
10: """
the rain came on time and the fields are green
we will start the harvest next week if weather stays
i planted rice and corn in the lower field
the cow gave less milk this morning than yesterday
can you help me carry the sacks to the market
the price of wheat is good this season
i need more water for the vegetable garden
the tractor broke down in the middle of work
we cut the grass for the animals this evening
the farmers meeting is at the village school tomorrow
the seeds were expensive but the crop looks healthy
i woke up early to feed the goats
the river is full and the fields are wet
my father taught me how to plant tomatoes
there are too many insects on the cabbage leaves
we sold all the potatoes at a fair price
the harvest festival is coming and everyone is busy
i will take the buffalo to the pond
the soil is rich and good for beans
please close the gate so the cows stay inside
it did not rain for two weeks and crops suffer
the neighbor lent me his plough for the day
i am saving money to buy a new tractor
the mangoes are ripe and ready to pick
we need strong rope to tie the bundles
the chickens laid many eggs this week again
the morning mist covers the whole valley today
can you bring tea to the field at noon
the wind was strong and it damaged the maize
i will sell the milk in the village tomorrow
the fruit trees need pruning before the winter comes
this year we got a better crop than last
the whole family works together in the field
the sun is hot so take a break
good soil good water and hard work give results
""",
11: """
we have band practice tonight at seven in the garage
i wrote a new song for the concert
can you tune the guitar before we start
the drummer is late again so we wait
our first show is on saturday at the cafe
i need a new set of strings
the crowd loved our last song so much
let us rehearse the chorus one more time
she has a beautiful voice and sings every morning
the sound system broke right before the show
i am learning to play the piano slowly
please turn down the volume i have a headache
we recorded the song and it sounds great
the lyrics are about home and old friends
can you play the bass line for me
my favorite band is coming to the city soon
i practice the guitar for two hours daily
the concert tickets sold out in just one day
we should post our new song online tonight
the microphone is not working so use mine
he plays the flute so well in the evening
i forgot the words in the middle of song
the audience clapped and asked for one more
let us write the next song together tomorrow
the new album will be out next month
i love the sound of the old piano
please bring your drums and cables to the show
our band name is finally ready for the poster
the rehearsal went well and everyone played perfectly tonight
can you sing the second part with me
i was so nervous before going on stage
the festival invited us to play on sunday
music makes me happy even on bad days
we need a better place for practice sessions
thanks for coming to our show tonight everyone
""",
12: """
the meeting starts at ten in the conference room
please send me the report before the end of day
my boss wants the presentation by tomorrow morning
i will join the call in five minutes
can you share the file on the shared drive
the deadline is friday so we need to hurry
i am working from home today because of rain
let us schedule a meeting for next week
the client was happy with our proposal yesterday
i need to reply to all these emails
can you review my draft and give feedback
the printer is not working again in office
we have a new manager starting on monday
i will be late because the traffic is terrible
please update the sheet with the latest numbers
the team lunch is on thursday at noon
i finished the budget and sent it to finance
the internet is slow so the call dropped
do you have the password for the system
i am taking a leave on friday afternoon
our company is hiring two new people this month
the quarterly results were better than we expected
can you cover for me during the lunch
i booked the room for the team meeting
let us finish this task before the weekend starts
the boss liked the idea and approved the plan
my desk is full of papers and files
we are launching the new product next quarter
please do not forget to sign the form
i will call the client and confirm the date
the office is quiet on fridays and relaxing
thank you for the feedback i will fix it
i am so busy that i skipped lunch
the training session starts at two in the afternoon
have a nice weekend and see you monday
""",
}

# ---- archive the old Holmes data so nothing is lost ----
archive = DATA / "holmes_archive"
archive.mkdir(exist_ok=True)
for f in (DATA / "clients").glob("holmes_*.txt"):
    shutil.move(str(f), archive / f.name)
for name in ("clean_corpus.txt", "val.txt"):
    if (DATA / name).exists() and not (archive / name).exists():
        shutil.copy(DATA / name, archive / name)

# ---- write each client's private training file; pool the held-out lines ----
(DATA / "clients").mkdir(exist_ok=True)
all_train, all_val = [], []
for cid, text in TEXTS.items():
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    train = [l for j, l in enumerate(lines) if j % 5 != 4]
    val = [l for j, l in enumerate(lines) if j % 5 == 4]
    (DATA / "clients" / f"client_{cid:02d}.txt").write_text("\n".join(train), encoding="utf-8")
    all_train += train
    all_val += val
    words = sum(len(l.split()) for l in train)
    print(f"client_{cid:02d}: {len(train)} train lines, {words} train words, {len(val)} val lines")

# pooled files are used ONLY by make_baseline.py (the centralized control experiment)
(DATA / "clean_corpus.txt").write_text("\n".join(all_train), encoding="utf-8")
(DATA / "val.txt").write_text("\n".join(all_val), encoding="utf-8")
print("total train lines:", len(all_train), "| val lines:", len(all_val))