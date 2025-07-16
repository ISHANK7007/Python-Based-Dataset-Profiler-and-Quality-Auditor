class ExplanationService:
    def generate_explanation(self, violation, context, verbosity="standard"):
        """Generate explanation at specified verbosity level"""
        # Base explanation is always generated
        terse = self._generate_terse_explanation(violation, context)
        
        if verbosity == "terse":
            return {
                "text": terse,
                "verbosity": "terse"
            }
        
        # Build standard explanation (builds on terse)
        standard = self._generate_standard_explanation(violation, context, terse)
        
        if verbosity == "standard":
            return {
                "text": standard,
                "verbosity": "standard",
                "terse": terse
            }
        
        # Build verbose explanation (builds on standard)
        verbose = self._generate_verbose_explanation(violation, context, standard)
        
        return {
            "text": verbose,
            "verbosity": "verbose",
            "standard": standard,
            "terse": terse
        }