from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Song
from .services import analyze_lyrics_with_gemini
from datetime import datetime
import logging

logger = logging.getLogger('lyrics_analyzer')


def index(request):
    logger.info(f"Index view accessed - Method: {request.method}, User authenticated: {request.user.is_authenticated}")
    
    if request.method == 'POST':
        lyrics = request.POST.get('lyrics', '').strip()
        logger.info(f"POST request with lyrics length: {len(lyrics) if lyrics else 0}")
        
        if lyrics:
            # Analyze lyrics with Gemini API
            logger.info("Starting Gemini API analysis")
            analysis = analyze_lyrics_with_gemini(lyrics)
            
            if analysis is None:
                # API failed - show error message instead of storing
                logger.error("Gemini API analysis failed")
                messages.error(request, "Sorry, there was an error analyzing your lyrics. Please try again later.")
                return redirect('index')
            
            logger.info(f"Analysis successful - sad_score: {analysis.get('sad_score')}, tags: {analysis.get('tags')}")
            sad_score = analysis['sad_score']
            tags = analysis['tags']
            description = analysis['description']
            
            if request.user.is_authenticated:
                # Save to database for logged-in users
                logger.info(f"Saving to database for user: {request.user.username}")
                try:
                    song = Song.objects.create(
                        user=request.user,
                        lyrics=lyrics,
                        sad_score=sad_score,
                        tags=tags,
                        description=description
                    )
                    logger.info(f"Song saved successfully with ID: {song.id}")
                except Exception as e:
                    logger.error(f"Database save failed: {str(e)}")
                    messages.error(request, "Sorry, there was an error saving your analysis. Please try again.")
                    return redirect('index')
            else:
                # Save to session for anonymous users
                logger.info("Saving to session for anonymous user")
                try:
                    analysis_result = {
                        'lyrics': lyrics,
                        'sad_score': sad_score,
                        'tags': tags,
                        'description': description,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    session_results = request.session.get('analysis_results', [])
                    session_results.append(analysis_result)
                    request.session['analysis_results'] = session_results
                    logger.info(f"Session updated - total results: {len(session_results)}")
                except Exception as e:
                    logger.error(f"Session save failed: {str(e)}")
                    messages.error(request, "Sorry, there was an error saving your analysis. Please try again.")
                    return redirect('index')
            
            # Redirect to prevent form resubmission
            logger.info("Redirecting after successful analysis")
            return redirect('index')
    
    # Get results based on user authentication
    logger.info("Retrieving results for display")
    try:
        if request.user.is_authenticated:
            logger.info(f"Querying database for user: {request.user.username}")
            results = Song.objects.filter(user=request.user)
            logger.info(f"Found {results.count()} songs in database")
        else:
            logger.info("Retrieving session results for anonymous user")
            session_results = request.session.get('analysis_results', [])
            results = sorted(session_results, key=lambda x: x['sad_score'], reverse=True)
            logger.info(f"Found {len(results)} results in session")
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}")
        results = []
        messages.error(request, "Sorry, there was an error loading your previous analyses.")
    
    logger.info("Rendering index template")
    return render(request, 'lyrics_analyzer/index.html', {
        'results': results
    })


def register(request):
    logger.info(f"Register view accessed - Method: {request.method}")
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            logger.info("Registration form is valid, creating user")
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                logger.info(f"User created successfully: {username}")
                messages.success(request, f'Account created for {username}!')
                
                # Auto-login after registration
                logger.info(f"Attempting auto-login for user: {username}")
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    logger.info(f"Auto-login successful for user: {username}")
                else:
                    logger.error(f"Auto-login failed for user: {username}")
                
                return redirect('index')
            except Exception as e:
                logger.error(f"User registration failed: {str(e)}")
                messages.error(request, "Sorry, there was an error creating your account. Please try again.")
        else:
            logger.warning(f"Registration form invalid: {form.errors}")
    else:
        form = UserCreationForm()
        logger.info("Displaying empty registration form")
    
    return render(request, 'lyrics_analyzer/register.html', {'form': form})
